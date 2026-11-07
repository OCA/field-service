# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentPortalOrderHistory(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "History Owner"})
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "portal-history@test.example.com",
                    "name": "Portal History User",
                    "partner_id": cls.partner.id,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal-history",
                }
            )
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {"name": "History Equipment", "owned_by_id": cls.partner.id}
        )
        cls.location = cls.env["fsm.location"].create(
            {"name": "History Location", "owner_id": cls.partner.id}
        )
        cls.order = cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
                "equipment_ids": [(4, cls.equipment.id)],
            }
        )

    def test_detail_page_shows_service_orders(self):
        self.authenticate("portal-history@test.example.com", "portal-history")
        response = self.url_open(f"/my/equipments/{self.equipment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Service Orders", response.content)
        self.assertIn(self.order.name.encode(), response.content)

    def test_detail_page_without_orders_hides_section(self):
        equipment = self.env["fsm.equipment"].create(
            {"name": "Orderless Equipment", "owned_by_id": self.partner.id}
        )
        self.authenticate("portal-history@test.example.com", "portal-history")
        response = self.url_open(f"/my/equipments/{equipment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Service Orders", response.content)
