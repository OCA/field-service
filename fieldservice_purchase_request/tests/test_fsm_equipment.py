# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestFSMEquipmentPurchaseRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["fsm.equipment"].create({"name": "Equipment"})
        cls.other_equipment = cls.env["fsm.equipment"].create({"name": "Other"})
        cls.order = cls.env["fsm.order"].create(
            {
                "location_id": cls.env.ref("fieldservice.test_location").id,
                "equipment_ids": [(4, cls.equipment.id)],
            }
        )
        cls.request = cls.env["purchase.request"].create({"fsm_order_id": cls.order.id})

    def test_purchase_request_count(self):
        self.assertEqual(self.equipment.purchase_request_count, 1)
        self.assertEqual(self.other_equipment.purchase_request_count, 0)

    def test_action_view_purchase_requests(self):
        action = self.equipment.action_view_purchase_requests()
        self.assertEqual(
            self.env["purchase.request"].search(action["domain"]), self.request
        )

    def test_fsm_user_without_purchase_request_group(self):
        user = self.env["res.users"].create(
            {
                "name": "fsm_no_pr",
                "login": "fsm_no_pr",
                "groups_id": [(6, 0, [self.env.ref("fieldservice.group_fsm_user").id])],
            }
        )
        equipment = self.equipment.with_user(user)
        arch = equipment.get_views([(False, "form")])["views"]["form"]["arch"]
        self.assertNotIn("purchase_request_count", arch)
        self.assertNotIn("purchase_request_count", equipment.fields_get())
