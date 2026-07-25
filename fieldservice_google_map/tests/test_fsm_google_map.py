# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestFSMGoogleMap(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Map Partner",
                "street": "1 Test Street",
                "city": "Test City",
                "partner_latitude": 45.5017,
                "partner_longitude": -73.5673,
            }
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Map Location",
                "owner_id": cls.partner.id,
            }
        )
        cls.location.partner_id.write(
            {
                "partner_latitude": 45.5017,
                "partner_longitude": -73.5673,
            }
        )
        cls.order = cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
            }
        )

    def test_location_marker_color(self):
        self.assertEqual(
            self.location.marker_color,
            self.location.stage_id.custom_color,
        )

    def test_order_map_fields(self):
        self.assertEqual(
            self.order.location_latitude,
            self.location.partner_latitude,
        )
        self.assertEqual(
            self.order.location_longitude,
            self.location.partner_longitude,
        )
        self.assertEqual(
            self.order.marker_color,
            self.order.stage_id.custom_color,
        )

    def test_map_views_and_actions(self):
        location_map = self.env.ref(
            "fieldservice_google_map.ir_ui_view_fsm_location_map"
        )
        order_map = self.env.ref("fieldservice_google_map.ir_ui_view_fsm_order_map")
        self.assertEqual(location_map.type, "google_map")
        self.assertEqual(order_map.type, "google_map")
        location_action = self.env.ref("fieldservice.action_fsm_location")
        order_action = self.env.ref("fieldservice.action_fsm_dash_order")
        self.assertIn("google_map", location_action.view_mode)
        self.assertIn("google_map", order_action.view_mode)
        self.assertIn("list", location_action.view_mode)
        self.assertIn("list", order_action.view_mode)
