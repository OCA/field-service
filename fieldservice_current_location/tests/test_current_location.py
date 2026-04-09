# Copyright 2025 APSL-Nagarro Bernat Obrador, Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests

from odoo.tests import common

PATCH_BASE = "odoo.addons.fieldservice_current_location.models.fsm_order"


class TestFieldserviceCrm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.location_1 = cls.env["fsm.location"].create(
            {
                "name": "Summer's House",
                "owner_id": cls.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )

        cls.fsm_user = cls.env["res.users"].create(
            {
                "name": "Fsm User",
                "login": "fsm_user",
                "groups_id": [(6, 0, [cls.env.ref("fieldservice.group_fsm_user").id])],
            }
        )
        cls.lat = 48.8584
        cls.lon = 2.2945

        # Fake location data returned by the geocoder
        cls.fake_place_id = 999999999
        cls.fake_location = SimpleNamespace(
            raw={
                "place_id": cls.fake_place_id,
                "address": {
                    "road": "Avenue Anatole France",
                    "house_number": "5",
                    "city": "Paris",
                    "town": None,
                    "village": None,
                    "city_block": None,
                    "postcode": "75007",
                    "country_code": "FR",
                    "province": "Île-de-France",
                },
            },
            address="5 Avenue Anatole France, 75007 Paris, France",
            latitude=cls.lat,
            longitude=cls.lon,
        )

    def test_save_location_from_browser(self):
        unique_id = uuid.uuid4().hex[:6]
        self.env["ir.config_parameter"].sudo().set_param(
            "nominatim.user_agent", f"Test-UA/1.0 ({unique_id})"
        )

        # Mock the geopy Nominatim geocoder and its reverse method
        with patch(f"{PATCH_BASE}.RateLimiter", lambda func, **kw: func), patch(
            f"{PATCH_BASE}.Nominatim"
        ) as nom_ctor:
            geolocator_mock = MagicMock()
            geolocator_mock.reverse.return_value = self.fake_location
            nom_ctor.return_value = geolocator_mock

            fsm_order = self.env["fsm.order"].create(
                {"location_id": self.location_1.id}
            )
            fsm_order.save_location_from_browser(self.lat, self.lon)

            self.assertEqual(fsm_order.location_id.city, "Paris")
            self.assertEqual(fsm_order.location_id.zip, "75007")

            # Should reuse existing location if place_id matches
            fsm_order2 = self.env["fsm.order"].create(
                {"location_id": self.location_1.id}
            )
            fsm_order2.save_location_from_browser(self.lat, self.lon)
            self.assertEqual(fsm_order2.location_id, fsm_order.location_id)
            # Verify that the user_agent was set correctly
            _, kwargs = nom_ctor.call_args
            self.assertEqual(kwargs.get("user_agent"), f"Test-UA/1.0 ({unique_id})")

    def test_generate_custom_user_agent(self):
        self.env["ir.config_parameter"].sudo().set_param("nominatim.user_agent", "")

        with patch(f"{PATCH_BASE}.RateLimiter", lambda func, **kw: func), patch(
            f"{PATCH_BASE}.Nominatim"
        ) as nom_ctor:
            geolocator_mock = MagicMock()
            geolocator_mock.reverse.return_value = self.fake_location
            nom_ctor.return_value = geolocator_mock

            fsm_order = self.env["fsm.order"].create(
                {"location_id": self.location_1.id}
            )
            fsm_order.save_location_from_browser(self.lat, self.lon)

            ua = (
                self.env["ir.config_parameter"].sudo().get_param("nominatim.user_agent")
            )
            self.assertTrue(ua)
            _, kwargs = nom_ctor.call_args
            self.assertEqual(kwargs.get("user_agent"), ua)

    def test_show_geolocate_button_no_restrict(self):
        # Without restrict config, button should always show
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice.restrict_current_location_in_templates", False
        )
        fsm_order = self.env["fsm.order"].create({"location_id": self.location_1.id})
        self.assertTrue(fsm_order.show_geolocate_button)

    def test_show_geolocate_button_with_restrict_no_template(self):
        # With restrict config, no template -> button hidden
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice.restrict_current_location_in_templates", True
        )
        fsm_order = self.env["fsm.order"].create({"location_id": self.location_1.id})
        self.assertFalse(fsm_order.show_geolocate_button)

    def test_show_geolocate_button_with_restrict_template_no_use_location(self):
        # With restrict config, template without use_current_location -> button hidden
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice.restrict_current_location_in_templates", True
        )
        template = self.env["fsm.template"].create(
            {"name": "Test Template", "use_current_location": False}
        )
        fsm_order = self.env["fsm.order"].create(
            {"location_id": self.location_1.id, "template_id": template.id}
        )
        self.assertFalse(fsm_order.show_geolocate_button)

    def test_show_geolocate_button_with_restrict_template_use_location(self):
        # With restrict config, template with use_current_location -> button shown
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice.restrict_current_location_in_templates", True
        )
        template = self.env["fsm.template"].create(
            {"name": "Test Template", "use_current_location": True}
        )
        fsm_order = self.env["fsm.order"].create(
            {"location_id": self.location_1.id, "template_id": template.id}
        )
        self.assertTrue(fsm_order.show_geolocate_button)

    def test_template_show_use_current_location_no_restrict(self):
        # Without restrict config, field should be hidden
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice.restrict_current_location_in_templates", False
        )
        template = self.env["fsm.template"].create({"name": "Test Template"})
        self.assertFalse(template.show_use_current_location)

    def test_config_parameter(self):
        # Test setting the config parameter
        self.env["res.config.settings"].create(
            {"restrict_current_location_in_templates": True}
        ).execute()
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fieldservice.restrict_current_location_in_templates")
        )
        self.assertTrue(param)
