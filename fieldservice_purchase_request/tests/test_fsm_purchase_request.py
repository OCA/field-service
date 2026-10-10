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
