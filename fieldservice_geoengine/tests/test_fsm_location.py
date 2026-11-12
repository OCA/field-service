# Copyright (C) 2012 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import Mock, patch

from lxml import etree

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestFsmLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.owner = cls.env["res.partner"].create({"name": "Geo Owner"})
        cls.delta = 0.00001

    def _location_vals(self, **extra):
        vals = {"name": "Geo Location", "owner_id": self.owner.id}
        vals.update(extra)
        return vals

    def test_shape_from_coordinates(self):
        location = self.env["fsm.location"].create(
            self._location_vals(partner_latitude=13.75, partner_longitude=100.50)
        )
        self.assertTrue(location.shape)
        order = self.env["fsm.order"].create({"location_id": location.id})
        self.assertEqual(order.shape, location.shape)
        self.assertFalse(order.worker_shape)
        worker = self.env["fsm.person"].create(
            {
                "name": "Geo Worker",
                "partner_latitude": 13.77,
                "partner_longitude": 100.49,
            }
        )
        order.person_id = worker
        self.assertTrue(worker.shape)
        self.assertEqual(order.worker_shape, worker.shape)
        order.geo_localize()
        location.partner_latitude = 14.0
        self.assertEqual(order.shape, location.shape)
        self.assertAlmostEqual(location.partner_longitude, 100.50, delta=self.delta)
        location.partner_latitude = False
        location.partner_longitude = False
        self.assertFalse(location.shape)

    def test_create_without_coordinates_geolocalizes(self):
        def _fake_geo_localize(partners):
            partners.write({"partner_latitude": 50.62998, "partner_longitude": 4.86337})
            return True

        with patch.object(
            type(self.env["res.partner"]), "geo_localize", _fake_geo_localize
        ):
            location = self.env["fsm.location"].create(self._location_vals())
        self.assertAlmostEqual(location.partner_latitude, 50.62998, delta=self.delta)
        self.assertAlmostEqual(location.partner_longitude, 4.86337, delta=self.delta)
        self.assertTrue(location.shape)

    def test_multi_create(self):
        def _fake_geo_localize(partners):
            for index, partner in enumerate(partners, start=1):
                partner.write(
                    {"partner_latitude": float(index), "partner_longitude": 2.0}
                )
            return True

        with patch.object(
            type(self.env["res.partner"]), "geo_localize", _fake_geo_localize
        ):
            locations = self.env["fsm.location"].create(
                [
                    self._location_vals(name=f"Geo Location {index}")
                    for index in range(2)
                ]
            )
        self.assertEqual(len(locations), 2)
        self.assertTrue(all(locations.mapped("shape")))

    def test_groups_and_map_views(self):
        user_group = self.env.ref("fieldservice.group_fsm_user_own")
        manager_group = self.env.ref("fieldservice.group_fsm_manager")
        self.assertIn(
            self.env.ref("base_geoengine.group_geoengine_user"),
            user_group.implied_ids,
        )
        self.assertIn(
            self.env.ref("base_geoengine.group_geoengine_admin"),
            manager_group.implied_ids,
        )
        order_map = self.env.ref("fieldservice_geoengine.ir_ui_view_fsm_order_map")
        location_map = self.env.ref(
            "fieldservice_geoengine.ir_ui_view_fsm_location_map"
        )
        self.assertEqual(order_map.type, "geoengine")
        self.assertEqual(location_map.type, "geoengine")
        self.assertTrue(
            self.env.ref("fieldservice.action_fsm_dash_order").view_mode.startswith(
                "geoengine"
            )
        )
        self.assertIn(
            "geoengine",
            self.env.ref("fieldservice.fsm_order_action_from_dashboard").view_mode,
        )
        person_action = self.env.ref("fieldservice.action_fsm_person")
        self.assertIn("kanban", person_action.view_mode)
        self.assertIn("geoengine", person_action.view_mode)
        self.assertEqual(
            self.env.ref("fieldservice_geoengine.ir_ui_view_fsm_person_map").type,
            "geoengine",
        )

    def test_vector_layer_domain_and_constraint(self):
        geo_field = self.env.ref("fieldservice_geoengine.field_fsm_location__shape")
        view = self.env.ref("fieldservice_geoengine.ir_ui_view_fsm_location_map")
        char_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("ttype", "=", "char")], limit=1
        )
        float_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("ttype", "=", "float")], limit=1
        )
        Layer = self.env["geoengine.vector.layer"]

        numeric = Layer.new(
            {
                "name": "Numeric range",
                "geo_repr": "colored",
                "classification": "interval",
                "geo_field_id": geo_field.id,
                "view_id": view.id,
            }
        )
        numeric._compute_attribute_field_id_domain()
        self.assertIn("integer", str(numeric.attribute_field_id_domain))

        unique = Layer.new(
            {
                "name": "Unique",
                "geo_repr": "colored",
                "classification": "unique",
                "geo_field_id": geo_field.id,
                "view_id": view.id,
            }
        )
        unique._compute_attribute_field_id_domain()
        self.assertIn("char", str(unique.attribute_field_id_domain))

        empty = Layer.new({"name": "Empty", "geo_repr": "basic"})
        empty._compute_attribute_field_id_domain()
        self.assertIn("char", str(empty.attribute_field_id_domain))
        self.assertNotIn("fsm.location", str(empty.attribute_field_id_domain))

        with self.assertRaises(ValidationError):
            Layer.new(
                {
                    "geo_repr": "proportion",
                    "attribute_field_id": char_field.id,
                }
            )._check_geo_repr()
        with self.assertRaises(ValidationError):
            Layer.new(
                {
                    "geo_repr": "colored",
                    "classification": "interval",
                    "attribute_field_id": char_field.id,
                }
            )._check_geo_repr()
        Layer.new(
            {
                "geo_repr": "colored",
                "classification": "unique",
                "attribute_field_id": char_field.id,
            }
        )._check_geo_repr()
        Layer.new(
            {
                "geo_repr": "proportion",
                "attribute_field_id": float_field.id,
            }
        )._check_geo_repr()
        Layer.new(
            {
                "geo_repr": "colored",
                "classification": "unique",
                "attribute_field_id": char_field.id,
                "geo_field_id": geo_field.id,
            }
        )._check_geo_repr()
        Layer.new(
            {
                "geo_repr": "proportion",
                "attribute_field_id": char_field.id,
                "geo_field_id": geo_field.id,
            }
        )._check_geo_repr()

    def test_location_can_store_an_area(self):
        location = self.env["fsm.location"].create(
            self._location_vals(partner_latitude=13.75, partner_longitude=100.50)
        )
        self.assertEqual(location.shape_kind, "point")
        location.shape_kind = "area"
        location.area_shape = (
            "POLYGON((100.49 13.74, 100.52 13.74, 100.52 13.77, "
            "100.49 13.77, 100.49 13.74))"
        )
        self.assertEqual(location.area_shape.geom_type, "Polygon")

    def test_dayroute_map_follows_order_sequence(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "code": "Ok",
            "routes": [
                {"geometry": {"coordinates": [[100.49, 13.77], [100.50, 13.73]]}}
            ],
        }
        self.env["fsm.team"].create({"name": "Geo Team"})
        person = self.env["fsm.person"].create(
            {
                "name": "Route Worker",
                "partner_latitude": 13.77,
                "partner_longitude": 100.49,
            }
        )
        route = self.env["fsm.route"].create(
            {"name": "Geo Route", "fsm_person_id": person.id}
        )
        dayroute = self.env["fsm.route.dayroute"].create(
            {"date": "2026-11-12", "route_id": route.id}
        )
        self.assertEqual(dayroute.person_id, person)
        early_location = self.env["fsm.location"].create(
            self._location_vals(
                name="Stop A", partner_latitude=13.73, partner_longitude=100.50
            )
        )
        late_location = self.env["fsm.location"].create(
            self._location_vals(
                name="Stop B", partner_latitude=13.80, partner_longitude=100.55
            )
        )
        late_order = self.env["fsm.order"].create({"location_id": late_location.id})
        early_order = self.env["fsm.order"].create({"location_id": early_location.id})
        late_order.write({"dayroute_id": dayroute.id})
        early_order.write({"dayroute_id": dayroute.id})
        late_order.sequence = 20
        early_order.sequence = 10
        with patch(
            "odoo.addons.fieldservice_geoengine.models.fsm_route_dayroute.requests.get",
            return_value=response,
        ):
            stops = dayroute.map_payload["stops"]
            self.assertEqual(
                [stop["name"] for stop in stops],
                [early_order.name, late_order.name],
            )
            self.assertEqual([stop["step"] for stop in stops], [1, 2])
            self.assertEqual(
                dayroute.map_payload["path"][0],
                [100.49, 13.77],
            )
            self.assertEqual(dayroute.map_payload["worker"]["name"], "Route Worker")
            self.assertAlmostEqual(
                dayroute.map_payload["worker"]["lat"], 13.77, delta=self.delta
            )
            early_order.stage_id = self.env.ref("fieldservice.fsm_stage_completed")
            stops = dayroute.map_payload["stops"]
        self.assertEqual(
            [stop["name"] for stop in stops if stop.get("step")],
            [late_order.name],
        )

    def test_optimize_orders_follows_driving_time(self):
        def trip_response(url, params=None, **kwargs):
            fixed_end = bool(params and params.get("destination") == "last")
            indexes = [0, 2, 1, 3] if fixed_end else [0, 2, 1]
            response = Mock()
            response.raise_for_status.return_value = None
            response.json.return_value = {
                "code": "Ok",
                "waypoints": [{"waypoint_index": index} for index in indexes],
            }
            return response

        self.env["fsm.team"].create({"name": "Optimize Team"})
        person = self.env["fsm.person"].create(
            {
                "name": "Optimize Worker",
                "partner_latitude": 33.45,
                "partner_longitude": -112.07,
            }
        )
        route = self.env["fsm.route"].create(
            {
                "name": "Optimize Route",
                "fsm_person_id": person.id,
                "max_order": 10,
                "day_ids": [
                    (6, 0, [self.env.ref("fieldservice_route.fsm_route_day_3").id])
                ],
            }
        )
        dayroute = self.env["fsm.route.dayroute"].create(
            {"date": "2026-11-12", "route_id": route.id}
        )
        done_location = self.env["fsm.location"].create(
            self._location_vals(
                name="Done", partner_latitude=33.44, partner_longitude=-112.08
            )
        )
        first = self.env["fsm.location"].create(
            self._location_vals(
                name="First", partner_latitude=33.50, partner_longitude=-112.10
            )
        )
        second = self.env["fsm.location"].create(
            self._location_vals(
                name="Second", partner_latitude=33.48, partner_longitude=-111.93
            )
        )
        missing = self.env["fsm.location"].create(self._location_vals(name="Missing"))
        (done_location | first | second | missing).fsm_route_id = route
        done = self.env["fsm.order"].create({"location_id": done_location.id})
        early = self.env["fsm.order"].create({"location_id": first.id})
        late = self.env["fsm.order"].create({"location_id": second.id})
        skipped = self.env["fsm.order"].create({"location_id": missing.id})
        orders = done | early | late | skipped
        orders.write({"dayroute_id": dayroute.id})
        done.stage_id = self.env.ref("fieldservice.fsm_stage_cancelled")
        done.sequence = 5
        early.sequence = 10
        late.sequence = 20
        skipped.sequence = 30
        with patch(
            "odoo.addons.fieldservice_geoengine.models.fsm_route_dayroute.requests.get",
            side_effect=trip_response,
        ) as get:
            dayroute.action_optimize_orders()
        params = get.call_args.kwargs["params"]
        self.assertEqual(params["source"], "first")
        self.assertEqual(params["roundtrip"], "false")
        self.assertNotIn("destination", params)
        self.assertIn("/trip/v1/driving/", get.call_args.args[0])
        self.assertEqual(done.sequence, 5)
        self.assertEqual(late.sequence, 15)
        self.assertEqual(early.sequence, 25)
        self.assertEqual(skipped.sequence, 35)
        failed = Mock()
        failed.raise_for_status.return_value = None
        failed.json.return_value = {"code": "NoRoute"}
        with patch(
            "odoo.addons.fieldservice_geoengine.models.fsm_route_dayroute.requests.get",
            return_value=failed,
        ):
            with self.assertRaises(UserError):
                dayroute.action_optimize_orders()
        dayroute.end_location_id = done_location
        with patch(
            "odoo.addons.fieldservice_geoengine.models.fsm_route_dayroute.requests.get",
            side_effect=trip_response,
        ) as get:
            dayroute.action_optimize_orders()
        self.assertEqual(get.call_args.kwargs["params"]["destination"], "last")
        arch = etree.fromstring(
            self.env["fsm.route.dayroute"].get_view(view_type="form")["arch"]
        )
        self.assertIsNotNone(arch.find(".//button[@name='action_optimize_orders']"))

    def _mercator_box(self, longitude, latitude, delta=0.05):
        wkt = (
            f"POLYGON(({longitude - delta} {latitude - delta}, "
            f"{longitude + delta} {latitude - delta}, "
            f"{longitude + delta} {latitude + delta}, "
            f"{longitude - delta} {latitude + delta}, "
            f"{longitude - delta} {latitude - delta}))"
        )
        self.env.cr.execute(
            "SELECT ST_AsText(ST_Transform(ST_GeomFromText(%s, 4326), 3857))",
            (wkt,),
        )
        return self.env.cr.fetchone()[0]

    def test_route_area_assigns_locations(self):
        inside = self.env["fsm.location"].create(
            self._location_vals(
                name="Inside", partner_latitude=13.75, partner_longitude=100.50
            )
        )
        outside = self.env["fsm.location"].create(
            self._location_vals(
                name="Outside", partner_latitude=41.88, partner_longitude=-87.63
            )
        )
        route = self.env["fsm.route"].create(
            {
                "name": "Area Route",
                "area_shape": self._mercator_box(100.50, 13.75),
            }
        )
        self.assertEqual(inside.fsm_route_id, route)
        self.assertFalse(outside.fsm_route_id)
        self.assertEqual(route.location_count, 1)
        action = route.action_view_locations()
        self.assertEqual(action["res_model"], "fsm.location")
        self.assertEqual(action["domain"], [("fsm_route_id", "=", route.id)])
        outside.write({"partner_latitude": 13.76, "partner_longitude": 100.51})
        self.assertEqual(outside.fsm_route_id, route)
        route.area_shape = False
        self.assertFalse(inside.fsm_route_id)
        self.assertFalse(outside.fsm_route_id)
        self.assertEqual(route.location_count, 0)

    def test_map_labels(self):
        location_arch = etree.fromstring(
            self.env["fsm.location"].get_view(view_type="form")["arch"]
        )
        person_arch = etree.fromstring(
            self.env["fsm.person"].get_view(view_type="form")["arch"]
        )
        route_arch = etree.fromstring(
            self.env["fsm.route"].get_view(view_type="form")["arch"]
        )
        self.assertEqual(
            location_arch.find(".//page[@name='geo_location']").get("string"),
            "Map",
        )
        self.assertEqual(
            person_arch.find(".//page[@name='geo_location']").get("string"),
            "Map",
        )
        preferred = person_arch.xpath("//page[field[@name='location_ids']]")
        self.assertEqual(preferred[0].get("string"), "Preferred Locations")
        self.assertIsNotNone(person_arch.find(".//field[@name='preferred_route_id']"))
        self.assertEqual(route_arch.find(".//page[@name='map']").get("string"), "Map")
        self.assertIsNotNone(route_arch.find(".//chatter"))
        dayroute_arch = etree.fromstring(
            self.env["fsm.route.dayroute"].get_view(view_type="form")["arch"]
        )
        self.assertIsNotNone(dayroute_arch.find(".//chatter"))
        self.assertIsNotNone(route_arch.find(".//field[@name='location_count']"))
        self.assertEqual(
            self.env.ref("fieldservice_geoengine.geoengine_vector_layer_fsm0").name,
            "Location",
        )

    def test_dayroute_dashboard_has_a_map(self):
        action = self.env.ref("fieldservice_route.action_fsm_route_dayroute_dash")
        self.assertTrue(action.view_mode.startswith("dayroute_map"))
        view = self.env.ref("fieldservice_geoengine.fsm_route_dayroute_dashboard_map")
        self.assertEqual(view.type, "dayroute_map")
        self.assertEqual(view.model, "fsm.route.dayroute")
