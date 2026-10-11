# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


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

    def _auth(self):
        self.authenticate("portal-create@test.example.com", "portal-create")

    def test_location_flow(self):
        # No address fields on purpose: with fieldservice_geoengine installed
        # (whole-repo CI), an address triggers geocoding on create and the
        # test framework blocks external HTTP requests, failing the submit.
        self._auth()
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

    def test_equipment_flow_creates_lot_under_product(self):
        self._auth()
        location = self.env["fsm.location"].create(
            {"name": "Existing Clinic", "owner_id": self.partner.id}
        )
        response = self.url_open("/my/equipments/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registrable Device", response.content)
        response = self.url_open(
            "/my/equipments/submit",
            data={
                "name": "New Device",
                "location_id": location.id,
                "product_id": self.product.id,
                "serial": "PORTAL-SN-1",
                "csrf_token": http_csrf(self),
            },
        )
        equipment = self.env["fsm.equipment"].search(
            [("name", "=", "New Device - PORTAL-SN-1")]
        )
        self.assertTrue(equipment)
        self.assertEqual(equipment.owned_by_id, self.partner)
        self.assertEqual(equipment.product_id, self.product)
        self.assertEqual(equipment.lot_id.product_id, self.product)
        self.assertEqual(equipment.lot_id.name, "PORTAL-SN-1")

    def test_equipment_flow_reuses_existing_lot(self):
        self._auth()
        location = self.env["fsm.location"].create(
            {"name": "Clinic 2", "owner_id": self.partner.id}
        )
        lot = self.env["stock.lot"].create(
            {"name": "PORTAL-SN-2", "product_id": self.product.id}
        )
        self.url_open(
            "/my/equipments/submit",
            data={
                "name": "Device 2",
                "location_id": location.id,
                "product_id": self.product.id,
                "serial": "PORTAL-SN-2",
                "csrf_token": http_csrf(self),
            },
        )
        equipment = self.env["fsm.equipment"].search(
            [("name", "=", "Device 2 - PORTAL-SN-2")]
        )
        self.assertEqual(equipment.lot_id, lot)


def http_csrf(case):
    """Fetch a CSRF token valid for the authenticated session."""
    return (
        case.opener.get(case.base_url() + "/my/locations/new")
        .text.split('name="csrf_token"')[1]
        .split('value="')[1]
        .split('"')[0]
    )
