# Copyright (C) 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/"
OSRM_TRIP_URL = "https://router.project-osrm.org/trip/v1/driving/"


class FSMRouteDayroute(models.Model):
    _name = "fsm.route.dayroute"
    _inherit = ["fsm.route.dayroute", "mail.thread", "mail.activity.mixin"]

    map_payload = fields.Json(
        compute="_compute_map_payload",
        string="Map",
    )

    def _map_stop(self, order):
        location = order.location_id
        latitude = location.partner_latitude
        longitude = location.partner_longitude
        if not latitude and not longitude:
            return False
        return {
            "name": order.name,
            "sequence": order.sequence,
            "lat": latitude,
            "lon": longitude,
        }

    def _orders_from_first_open(self, orders):
        """Open order with the lowest sequence, and every order after it."""
        orders = orders.sorted(key=lambda order: (order.sequence, order.id))
        for index, order in enumerate(orders):
            if not order.stage_id.is_closed:
                return orders[index:]
        return self.env["fsm.order"]

    def _osrm_path(self, points):
        """Street path through [longitude, latitude] points. Empty on failure."""
        if len(points) < 2:
            return []
        coord_path = ";".join(f"{lon},{lat}" for lon, lat in points)
        try:
            response = requests.get(
                f"{OSRM_ROUTE_URL}{coord_path}",
                params={"overview": "full", "geometries": "geojson"},
                headers={"User-Agent": "fieldservice-geoengine"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            _logger.warning("OSRM path failed for %s", self.display_name)
            return []
        routes = payload.get("routes") or []
        if payload.get("code") != "Ok" or not routes:
            return []
        geometry = routes[0].get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        return [pair[:2] for pair in coordinates if len(pair) >= 2]

    def _trip_end(self):
        """Fixed last stop when the day route has an end location."""
        self.ensure_one()
        location = self.end_location_id
        if not location or not (
            location.partner_latitude or location.partner_longitude
        ):
            return False
        return [location.partner_longitude, location.partner_latitude]

    def _osrm_trip(self, points, fixed_end=False):
        """Waypoint indexes that minimize driving time. Empty on failure.

        The first point is the fixed start. The public driving profile has no
        distance or cost objective.
        """
        if len(points) < 2:
            return []
        params = {
            "source": "first",
            "roundtrip": "false",
            "overview": "false",
        }
        if fixed_end:
            params["destination"] = "last"
        coord_path = ";".join(f"{lon},{lat}" for lon, lat in points)
        try:
            response = requests.get(
                f"{OSRM_TRIP_URL}{coord_path}",
                params=params,
                headers={"User-Agent": "fieldservice-geoengine"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            _logger.warning("OSRM trip failed for %s", self.display_name)
            return []
        waypoints = payload.get("waypoints") or []
        if payload.get("code") != "Ok" or len(waypoints) != len(points):
            return []
        indexes = [waypoint.get("waypoint_index") for waypoint in waypoints]
        if any(index is None for index in indexes):
            return []
        return indexes

    def action_optimize_orders(self):
        """Reorder open orders by driving time from the worker."""
        for route in self:
            route._optimize_orders()
        return True

    def _optimize_orders(self):
        self.ensure_one()
        worker = self._map_worker()
        if not worker:
            raise UserError(
                self.env._("Set the worker location before optimizing this day route.")
            )
        closed = self.order_ids.filtered(lambda order: order.stage_id.is_closed)
        located = []
        unlocated = []
        open_orders = (self.order_ids - closed).sorted(
            key=lambda order: (order.sequence, order.id)
        )
        for order in open_orders:
            if self._map_stop(order):
                located.append(order)
            else:
                unlocated.append(order)
        if len(located) < 2:
            raise UserError(
                self.env._("At least two open orders with a location are required.")
            )
        points = [[worker["lon"], worker["lat"]]]
        for order in located:
            stop = self._map_stop(order)
            points.append([stop["lon"], stop["lat"]])
        end = self._trip_end()
        if end:
            points.append(end)
        indexes = self._osrm_trip(points, fixed_end=bool(end))
        if not indexes:
            raise UserError(self.env._("OSRM could not optimize this day route."))
        order_indexes = indexes[1:-1] if end else indexes[1:]
        ranked = sorted(
            zip(located, order_indexes, strict=False),
            key=lambda item: (item[1], item[0].id),
        )
        base = max(closed.mapped("sequence") or [0])
        step = 0
        for step, (order, _index) in enumerate(ranked, start=1):
            order.sequence = base + step * 10
        for order in unlocated:
            step += 1
            order.sequence = base + step * 10

    def _map_worker(self):
        self.ensure_one()
        person = self.person_id
        if not person or not (person.partner_latitude or person.partner_longitude):
            return False
        return {
            "name": person.name,
            "lat": person.partner_latitude,
            "lon": person.partner_longitude,
        }

    @api.depends(
        "person_id",
        "person_id.partner_latitude",
        "person_id.partner_longitude",
        "person_id.name",
        "order_ids.sequence",
        "order_ids.name",
        "order_ids.location_id",
        "order_ids.location_id.partner_latitude",
        "order_ids.location_id.partner_longitude",
        "order_ids.stage_id",
        "order_ids.stage_id.is_closed",
    )
    def _compute_map_payload(self):
        for route in self:
            orders = route.order_ids.sorted(
                key=lambda order: (order.sequence, order.id)
            )
            remaining = route._orders_from_first_open(orders)
            remaining_ids = set(remaining.ids)
            stops = []
            step = 0
            points = []
            worker = route._map_worker()
            if worker:
                points.append([worker["lon"], worker["lat"]])
            for order in orders:
                stop = route._map_stop(order)
                if not stop:
                    continue
                if order.id in remaining_ids:
                    step += 1
                    stop["step"] = step
                    points.append([stop["lon"], stop["lat"]])
                stops.append(stop)
            route.map_payload = {
                "stops": stops,
                "path": route._osrm_path(points),
                "worker": worker,
            }
