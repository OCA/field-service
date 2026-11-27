# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import HttpCase, tagged

from odoo.addons.fieldservice_equipment_portal_create.controllers.main import (
    PortalEquipmentCreate,
)


@tagged("post_install", "-at_install")
class TestEquipmentPortalCreate(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Hospital Partner"})
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "portal-create@test.example.com",
                    "name": "Portal Create User",
                    "partner_id": cls.partner.id,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal-create",
                }
            )
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Registrable Device",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        # No address fields on purpose: with fieldservice_geoengine installed
        # (whole-repo CI), an address triggers geocoding on create and the
        # test framework blocks external HTTP requests.
        cls.location = cls.env["fsm.location"].create(
            {"name": "Existing Clinic", "owner_id": cls.partner.id}
        )

    def setUp(self):
        super().setUp()
        self.authenticate("portal-create@test.example.com", "portal-create")

    def _submit_equipment(self, **values):
        data = {
            "name": "New Device",
            "location_id": self.location.id,
            "product_id": self.product.id,
            "serial": "PORTAL-SN-1",
        }
        data.update(values)
        data["csrf_token"] = http_csrf(self)
        return self.url_open("/my/equipments/submit", data=data)

    def _equipments(self, name):
        return self.env["fsm.equipment"].search([("name", "=", name)])

    def test_location_flow_attaches_to_root_location(self):
        response = self.url_open("/my/locations/new")
        self.assertEqual(response.status_code, 200)
        response = self.url_open(
            "/my/locations/submit",
            data={
                "name": "Portal Clinic",
                "phone": "555-1234",
                "csrf_token": http_csrf(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        location = self.env["fsm.location"].search([("name", "=", "Portal Clinic")])
        self.assertTrue(location)
        self.assertEqual(location.owner_id, self.partner)
        self.assertEqual(location.phone, "555-1234")
        self.assertEqual(location.parent_id, self.location)

    def test_location_without_root_location(self):
        self.location.owner_id = self.env["res.partner"].create({"name": "Other"})
        self.url_open(
            "/my/locations/submit",
            data={"name": "First Clinic", "csrf_token": http_csrf(self)},
        )
        location = self.env["fsm.location"].search([("name", "=", "First Clinic")])
        self.assertEqual(location.owner_id, self.partner)
        self.assertFalse(location.parent_id)

    def test_location_requires_name(self):
        count = self.env["fsm.location"].search_count([])
        response = self.url_open(
            "/my/locations/submit",
            data={"name": " ", "phone": "555-9876", "csrf_token": http_csrf(self)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The location name is required.", response.content)
        self.assertIn(b"555-9876", response.content)
        self.assertEqual(self.env["fsm.location"].search_count([]), count)

    def test_equipment_flow_creates_lot_under_product(self):
        response = self.url_open("/my/equipments/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registrable Device", response.content)
        response = self._submit_equipment()
        equipment = self._equipments("New Device - PORTAL-SN-1")
        self.assertTrue(equipment)
        self.assertEqual(equipment.owned_by_id, self.partner)
        self.assertEqual(equipment.location_id, self.location)
        self.assertEqual(equipment.product_id, self.product)
        self.assertEqual(equipment.company_id, self.portal_user.company_id)
        self.assertEqual(equipment.lot_id.product_id, self.product)
        self.assertEqual(equipment.lot_id.name, "PORTAL-SN-1")
        self.assertEqual(equipment.lot_id.company_id, equipment.company_id)
        self.assertEqual(equipment.lot_id.fsm_equipment_id, equipment)
        # the redirect opens the equipment page for its portal owner
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.url.endswith(f"/my/equipments/{equipment.id}"))
        self.assertIn(b"New Device - PORTAL-SN-1", response.content)

    def test_equipment_flow_reuses_free_lot(self):
        lot = self.env["stock.lot"].create(
            {"name": "PORTAL-SN-2", "product_id": self.product.id}
        )
        self._submit_equipment(name="Device 2", serial="PORTAL-SN-2")
        self.assertEqual(self._equipments("Device 2 - PORTAL-SN-2").lot_id, lot)

    def test_equipment_flow_ignores_lot_of_other_company(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        other_lot = self.env["stock.lot"].create(
            {
                "name": "PORTAL-SN-3",
                "product_id": self.product.id,
                "company_id": other_company.id,
            }
        )
        self._submit_equipment(name="Device 3", serial="PORTAL-SN-3")
        lot = self._equipments("Device 3 - PORTAL-SN-3").lot_id
        self.assertTrue(lot)
        self.assertNotEqual(lot, other_lot)
        self.assertEqual(lot.company_id, self.portal_user.company_id)

    def test_equipment_rejects_lot_of_another_equipment(self):
        lot = self.env["stock.lot"].create(
            {"name": "PORTAL-SN-4", "product_id": self.product.id}
        )
        first = self.env["fsm.equipment"].create(
            {
                "name": "Registered Device",
                "product_id": self.product.id,
                "lot_id": lot.id,
            }
        )
        response = self._submit_equipment(name="Copy", serial="PORTAL-SN-4")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"The serial number PORTAL-SN-4 is already registered.", response.content
        )
        self.assertFalse(self._equipments("Copy - PORTAL-SN-4"))
        self.assertEqual(lot.fsm_equipment_id, first)

    def test_equipment_rejects_repeated_name(self):
        self._submit_equipment(name="Twin", serial="PORTAL-SN-5")
        lot_count = self.env["stock.lot"].search_count([])
        response = self._submit_equipment(name="Twin", serial="PORTAL-SN-5")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"already exists", response.content)
        self.assertEqual(len(self._equipments("Twin - PORTAL-SN-5")), 1)
        self.assertEqual(self.env["stock.lot"].search_count([]), lot_count)

    def test_equipment_rejects_location_of_another_partner(self):
        foreign = self.env["fsm.location"].create(
            {
                "name": "Foreign Clinic",
                "owner_id": self.env["res.partner"].create({"name": "Foreign"}).id,
            }
        )
        lot_count = self.env["stock.lot"].search_count([])
        response = self._submit_equipment(location_id=foreign.id)
        self.assertIn(b"Select one of your locations.", response.content)
        self.assertFalse(self._equipments("New Device - PORTAL-SN-1"))
        self.assertEqual(self.env["stock.lot"].search_count([]), lot_count)

    def test_equipment_rejects_product_not_registrable(self):
        untracked = self.env["product.product"].create(
            {"name": "Untracked Device", "is_storable": True}
        )
        response = self._submit_equipment(product_id=untracked.id)
        self.assertIn(b"Select one of the products offered.", response.content)
        response = self._submit_equipment(product_id="not-an-id")
        self.assertIn(b"Select one of the products offered.", response.content)
        self.assertFalse(self._equipments("New Device - PORTAL-SN-1"))

    def test_equipment_requires_serial(self):
        response = self._submit_equipment(serial=" ")
        self.assertIn(b"The name and the serial number are required.", response.content)
        # the typed values stay on the form
        self.assertIn(b"New Device", response.content)

    def test_product_search_and_limit(self):
        self.env["product.product"].create(
            {
                "name": "Another Device",
                "default_code": "XYZ-PORTAL",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        response = self.url_open("/my/equipments/new?search=XYZ-PORTAL")
        self.assertIn(b"Another Device", response.content)
        self.assertNotIn(b"Registrable Device", response.content)
        self.assertNotIn(b"search to narrow them", response.content)
        with patch.object(PortalEquipmentCreate, "_products_limit", 1):
            response = self.url_open("/my/equipments/new")
        self.assertIn(b"search to narrow them", response.content)


def http_csrf(case):
    """Fetch a CSRF token valid for the authenticated session."""
    return (
        case.opener.get(case.base_url() + "/my/locations/new")
        .text.split('name="csrf_token"')[1]
        .split('value="')[1]
        .split('"')[0]
    )
