# Copyright 2026 Antoni Marroig (APSL-Nagarro) <antoni.marroig@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import quote_plus

from odoo import api, fields, models
from odoo.tools import float_compare, html2plaintext

LOAD_SHEET_DEPENDS = (
    "order_ids",
    "order_ids.sequence",
    "order_ids.stage_id",
    "order_ids.description",
    "order_ids.location_id",
    "order_ids.location_id.notes",
    "order_ids.location_id.phone",
    "order_ids.location_id.mobile",
    "order_ids.location_id.street",
    "order_ids.location_id.street2",
    "order_ids.location_id.zip",
    "order_ids.location_id.city",
    "order_ids.location_id.state_id",
    "order_ids.location_id.country_id",
    "order_ids.picking_ids",
    "order_ids.picking_ids.move_ids",
    "order_ids.picking_ids.move_ids.state",
    "order_ids.picking_ids.move_ids.location_id",
    "order_ids.picking_ids.move_ids.location_dest_id",
    "order_ids.picking_ids.move_ids.product_id",
    "order_ids.picking_ids.move_ids.product_id.weight",
    "order_ids.picking_ids.move_ids.product_uom",
    "order_ids.picking_ids.move_ids.product_uom_qty",
    "order_ids.picking_ids.move_ids.quantity",
)


class FSMRouteDayRoute(models.Model):
    _inherit = "fsm.route.dayroute"

    summary_line_ids = fields.One2many(
        "fsm.route.dayroute.product.summary",
        "dayroute_id",
        string="Products to Load",
        readonly=True,
    )
    total_weight = fields.Float(
        string="Total Weight to Load",
        digits="Stock Weight",
        compute="_compute_total_weight",
    )
    weight_uom_name = fields.Char(
        string="Weight Unit", compute="_compute_weight_uom_name"
    )
    location_breakdown_html = fields.Html(
        string="Delivery Breakdown",
        compute="_compute_location_breakdown_html",
        sanitize=False,
    )

    @api.depends(*LOAD_SHEET_DEPENDS)
    def _compute_total_weight(self):
        for dayroute in self:
            dayroute.total_weight = sum(
                quantity * product.weight
                for product, quantity in dayroute._get_load_sheet_totals().items()
            )

    def _compute_weight_uom_name(self):
        weight_uom_name = self.env[
            "product.template"
        ]._get_weight_uom_name_from_ir_config_parameter()
        for dayroute in self:
            dayroute.weight_uom_name = weight_uom_name

    @api.depends(*LOAD_SHEET_DEPENDS)
    def _compute_location_breakdown_html(self):
        for dayroute in self:
            dayroute.location_breakdown_html = self.env["ir.qweb"]._render(
                "fieldservice_route_dayroute_summary.dayroute_location_cards",
                {"stops": dayroute._get_load_sheet_stops()},
            )

    def _get_load_sheet_orders(self):
        """Orders of the day route to deliver, in route order."""
        self.ensure_one()
        return self.order_ids.filtered(
            lambda order: not order._is_excluded_from_load_sheet()
        ).sorted(lambda order: (order.sequence, order._origin.id or 0))

    def _get_load_sheet_summary_lines(self):
        """Return the products to load read from the database, so they are up
        to date even when the orders changed in the current transaction."""
        self.ensure_one()
        Summary = self.env["fsm.route.dayroute.product.summary"]
        Summary.invalidate_model()
        return Summary.search([("dayroute_id", "=", self.id)])

    def _get_load_sheet_totals(self):
        """Return the quantity to deliver of each product, in the product unit
        of measure, as a ``{product: quantity}`` dict."""
        self.ensure_one()
        totals = {}
        for order in self._get_load_sheet_orders():
            for move in order._get_load_sheet_moves():
                if move.state == "done" or not move._is_load_sheet_delivery():
                    continue
                totals.setdefault(move.product_id, 0.0)
                totals[move.product_id] += move.product_qty
        return totals

    def _get_load_sheet_stops(self):
        """Return the values to render one card per order of the day route."""
        self.ensure_one()
        stops = []
        for index, order in enumerate(self._get_load_sheet_orders(), 1):
            location = order.location_id
            address = self._get_load_sheet_address(location)
            stops.append(
                {
                    "index": index,
                    "order": order,
                    "location": location,
                    "address": address,
                    "map_url": address
                    and "https://www.google.com/maps/search/?api=1&query="
                    + quote_plus(address),
                    "phone": location.phone,
                    "mobile": location.mobile,
                    "note": self._get_load_sheet_note(order),
                    "url": self._get_load_sheet_order_url(order),
                    "is_completed": order.is_closed,
                    "lines": [
                        self._get_load_sheet_move_values(move)
                        for move in order._get_load_sheet_moves()
                    ],
                }
            )
        return stops

    @api.model
    def _get_load_sheet_move_values(self, move):
        is_done = move.state == "done"
        is_pickup = move._is_load_sheet_pickup()
        return {
            "product": move.product_id,
            "quantity": move.quantity if is_done else move.product_uom_qty,
            "uom": move.product_uom,
            "is_pickup": is_pickup,
            # Deliveries without enough stock reserved to load them
            "is_missing_stock": not is_done
            and not is_pickup
            and float_compare(
                move.quantity,
                move.product_uom_qty,
                precision_rounding=move.product_uom.rounding,
            )
            < 0,
        }

    @api.model
    def _get_load_sheet_address(self, location):
        if not location:
            return ""
        address = location.partner_id._display_address(without_company=True)
        return ", ".join(part.strip() for part in address.split("\n") if part.strip())

    @api.model
    def _get_load_sheet_note(self, order):
        """Notes of the order or, when it has none, the ones of its location."""
        for note in (order.description, order.location_id.notes):
            text = html2plaintext(note or "").strip()
            if text:
                return text
        return ""

    def _get_load_sheet_order_url(self, order):
        """Link to the order keeping the day route in the breadcrumbs."""
        self.ensure_one()
        order_id = order._origin.id
        action = self.env.ref(
            "fieldservice_route.action_fsm_route_dayroute", raise_if_not_found=False
        )
        if action and self._origin.id:
            return f"/odoo/action-{action.id}/{self._origin.id}/fsm.order/{order_id}"
        return f"/odoo/fsm.order/{order_id}"
