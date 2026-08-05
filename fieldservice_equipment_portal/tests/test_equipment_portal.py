# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Equipment Owner"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Other Owner"})
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "portal-equipment@test.example.com",
                    "name": "Portal Equipment User",
                    "partner_id": cls.partner.id,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal-equipment",
                }
            )
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {"name": "My Portal Equipment", "owned_by_id": cls.partner.id}
        )
        cls.other_equipment = cls.env["fsm.equipment"].create(
            {"name": "Foreign Equipment", "owned_by_id": cls.other_partner.id}
        )

    def test_access_url(self):
        self.assertEqual(
            self.equipment.access_url, f"/my/equipments/{self.equipment.id}"
        )

    def test_portal_list_shows_own_equipments_only(self):
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        response = self.url_open("/my/equipments")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Portal Equipment", response.content)
        self.assertNotIn(b"Foreign Equipment", response.content)

    def test_portal_detail_page(self):
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        response = self.url_open(f"/my/equipments/{self.equipment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Portal Equipment", response.content)

    def test_portal_detail_denied_without_access(self):
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        response = self.url_open(f"/my/equipments/{self.other_equipment.id}")
        self.assertNotIn(b"Foreign Equipment", response.content)

    def test_portal_detail_with_access_token(self):
        self.other_equipment._portal_ensure_token()
        response = self.url_open(
            f"/my/equipments/{self.other_equipment.id}"
            f"?access_token={self.other_equipment.access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Foreign Equipment", response.content)

    def test_home_counter(self):
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        result = self.make_jsonrpc_request(
            "/my/counters", {"counters": ["equipment_count"]}
        )
        self.assertEqual(result["equipment_count"], 1)

    def test_list_and_counter_without_read_access(self):
        self.env.ref(
            "fieldservice_equipment_portal.access_fsm_equipment_portal"
        ).perm_read = False
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        response = self.url_open("/my/equipments")
        self.assertTrue(response.url.rstrip("/").endswith("/my"))
        result = self.make_jsonrpc_request(
            "/my/counters", {"counters": ["equipment_count"]}
        )
        self.assertEqual(result["equipment_count"], 0)

    def test_sort_by_name(self):
        self.authenticate("portal-equipment@test.example.com", "portal-equipment")
        response = self.url_open("/my/equipments?sortby=name")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Portal Equipment", response.content)
