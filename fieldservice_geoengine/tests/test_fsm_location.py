# Copyright (C) 2012 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import ValidationError
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
        self.assertIn(
            "geoengine", self.env.ref("fieldservice.action_fsm_dash_order").view_mode
        )
        self.assertIn(
            "geoengine",
            self.env.ref("fieldservice.fsm_order_action_from_dashboard").view_mode,
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
