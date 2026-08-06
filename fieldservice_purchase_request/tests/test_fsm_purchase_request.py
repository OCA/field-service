# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestFsmPurchaseRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["fsm.order"].create(
            {"location_id": cls.env.ref("fieldservice.test_location").id}
        )

    def test_create_purchase_request_from_order(self):
        action = self.order.action_create_purchase_request()
        request = self.env["purchase.request"].browse(action["res_id"])
        self.assertEqual(request.fsm_order_id, self.order)
        self.assertEqual(request.origin, self.order.name)
        self.assertEqual(self.order.purchase_request_count, 1)
        self.assertEqual(self.order.purchase_request_ids, request)

    def test_view_purchase_requests_action(self):
        self.order.action_create_purchase_request()
        action = self.order.action_view_purchase_requests()
        self.assertEqual(action["domain"], [("fsm_order_id", "=", self.order.id)])
        self.assertEqual(action["context"]["default_fsm_order_id"], self.order.id)

    def test_unlink_order_keeps_request(self):
        action = self.order.action_create_purchase_request()
        request = self.env["purchase.request"].browse(action["res_id"])
        self.order.unlink()
        self.assertTrue(request.exists())
        self.assertFalse(request.fsm_order_id)

    def _new_user(self, login, groups):
        return self.env["res.users"].create(
            {
                "name": login,
                "login": login,
                "groups_id": [(6, 0, [self.env.ref(g).id for g in groups])],
            }
        )

    def _form_arch(self, user):
        views = self.env["fsm.order"].with_user(user).get_views([(False, "form")])
        return views["views"]["form"]["arch"]

    def test_fsm_user_without_purchase_request_group(self):
        self.order.action_create_purchase_request()
        user = self._new_user("fsm_no_pr", ["fieldservice.group_fsm_user"])
        arch = self._form_arch(user)
        self.assertNotIn("purchase_request_count", arch)
        self.assertNotIn("action_create_purchase_request", arch)
        fields = self.env["fsm.order"].with_user(user).fields_get()
        self.assertNotIn("purchase_request_count", fields)
        order = self.order.with_user(user)
        self.assertEqual(order.read(["name"])[0]["name"], self.order.name)

    def test_purchase_request_user_sees_buttons(self):
        user = self._new_user(
            "fsm_pr",
            [
                "fieldservice.group_fsm_user",
                "purchase_request.group_purchase_request_user",
            ],
        )
        arch = self._form_arch(user)
        self.assertIn("purchase_request_count", arch)
        self.assertIn("action_create_purchase_request", arch)
        order = self.order.with_user(user)
        order.action_create_purchase_request()
        self.assertEqual(order.purchase_request_count, 1)

    def test_purchase_request_follows_order_company(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create({"name": "FSM PR Company B"})
        location_b = self.env["fsm.location"].create(
            {
                "name": "Location B",
                "owner_id": self.env.ref("base.res_partner_1").id,
                "company_id": company_b.id,
            }
        )
        stage_b = self.env["fsm.stage"].create(
            {
                "name": "New B",
                "stage_type": "order",
                "is_default": True,
                "sequence": 999,
                "company_id": company_b.id,
            }
        )
        team_b = self.env["fsm.team"].create(
            {"name": "Team B", "company_id": company_b.id}
        )
        order_b = (
            self.env["fsm.order"]
            .with_company(company_b)
            .create(
                {
                    "location_id": location_b.id,
                    "company_id": company_b.id,
                    "stage_id": stage_b.id,
                    "team_id": team_b.id,
                }
            )
        )
        user = self._new_user(
            "fsm_pr_mc",
            [
                "fieldservice.group_fsm_user",
                "purchase_request.group_purchase_request_user",
            ],
        )
        user.write(
            {
                "company_ids": [(6, 0, (company_a | company_b).ids)],
                "company_id": company_a.id,
            }
        )
        order = order_b.with_user(user).with_context(
            allowed_company_ids=[company_a.id, company_b.id]
        )
        self.assertEqual(order.env.company, company_a)
        action = order.action_create_purchase_request()
        request = self.env["purchase.request"].browse(action["res_id"])
        self.assertEqual(request.company_id, company_b)
        self.assertEqual(request.picking_type_id.warehouse_id.company_id, company_b)
