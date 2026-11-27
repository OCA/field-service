# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentPortalOrderHistory(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.has_portal_stages = "portal_visible" in cls.env["fsm.stage"]._fields
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
        if cls.has_portal_stages:
            cls.order.stage_id.portal_visible = True

    def _open_equipment(self, equipment, access_token=None):
        url = f"/my/equipments/{equipment.id}"
        if access_token:
            url = f"{url}?access_token={access_token}"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_admin_sees_service_orders(self):
        self.authenticate("admin", "admin")
        response = self._open_equipment(self.equipment)
        self.assertIn(b"Service Orders", response.content)
        self.assertIn(self.order.name.encode(), response.content)

    def test_portal_user_sees_orders_only_with_read_access(self):
        self.authenticate("portal-history@test.example.com", "portal-history")
        response = self._open_equipment(self.equipment)
        if self.env["fsm.order"].with_user(self.portal_user).has_access("read"):
            # fieldservice_portal grants portal users their own orders
            self.assertIn(self.order.name.encode(), response.content)
        else:
            self.assertNotIn(b"Service Orders", response.content)

    def test_portal_user_does_not_see_hidden_stage(self):
        if not self.has_portal_stages:
            self.skipTest("fieldservice_portal is not installed")
        hidden_stage = self.env["fsm.stage"].create(
            {
                "name": "Hidden From Portal",
                "stage_type": "order",
                "sequence": 999,
                "portal_visible": False,
            }
        )
        self.order.stage_id = hidden_stage
        self.authenticate("portal-history@test.example.com", "portal-history")
        response = self._open_equipment(self.equipment)
        self.assertNotIn(self.order.name.encode(), response.content)

    def test_token_visitor_does_not_see_orders(self):
        token = self.equipment._portal_ensure_token()
        response = self._open_equipment(self.equipment, access_token=token)
        self.assertIn(self.equipment.name.encode(), response.content)
        self.assertNotIn(b"Service Orders", response.content)
        self.assertNotIn(self.order.name.encode(), response.content)

    def test_order_of_another_company_is_hidden(self):
        other_company = self.env["res.company"].create({"name": "Other History Co"})
        admin = self.env.ref("base.user_admin")
        admin.company_ids |= other_company
        other_order = self.env["fsm.order"].create(
            {"location_id": self.location.id, "company_id": other_company.id}
        )
        # bypass the order company compute to simulate an inconsistent link
        other_order.write({"equipment_ids": [(4, self.equipment.id)]})
        self.assertIn(self.equipment, other_order.equipment_ids)
        if self.has_portal_stages:
            other_order.stage_id.portal_visible = True
        self.authenticate("admin", "admin")
        self.opener.cookies["cids"] = f"{admin.company_id.id}-{other_company.id}"
        response = self._open_equipment(self.equipment)
        self.assertIn(self.order.name.encode(), response.content)
        self.assertNotIn(other_order.name.encode(), response.content)

    def test_detail_page_without_orders_hides_section(self):
        equipment = self.env["fsm.equipment"].create(
            {"name": "Orderless Equipment", "owned_by_id": self.partner.id}
        )
        self.authenticate("admin", "admin")
        response = self._open_equipment(equipment)
        self.assertNotIn(b"Service Orders", response.content)
