# Copyright (C) 2021 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFieldServicePurchase(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_supplierinfo_obj = cls.env["product.supplierinfo"]
        cls.fsm_person_obj = cls.env["fsm.person"]
        cls.purchase_order_obj = cls.env["purchase.order"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Test Vendor",
                "supplier_rank": 1,
            }
        )

    def test_worker_vendor_pricelist(self):
        fsm_person = self.fsm_person_obj.create({"name": "Test FSM Person"})

        supplierinfo = self.product_supplierinfo_obj.create(
            {
                "partner_id": fsm_person.partner_id.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "min_qty": 1.0,
                "price": 100,
            }
        )
        fsm_person.invalidate_recordset(["pricelist_count"])
        self.assertEqual(fsm_person.pricelist_count, 1)
        action = fsm_person.action_view_pricelists()
        self.assertEqual(action["res_id"], supplierinfo.id)

        self.product_supplierinfo_obj.create(
            {
                "partner_id": fsm_person.partner_id.id,
                "product_tmpl_id": self.product_2.product_tmpl_id.id,
                "min_qty": 2.0,
                "price": 200,
            }
        )
        fsm_person.invalidate_recordset(["pricelist_count"])
        self.assertEqual(fsm_person.pricelist_count, 2)
        action = fsm_person.action_view_pricelists()
        pricelist_ids = self.product_supplierinfo_obj.search(
            [("partner_id", "=", fsm_person.partner_id.id)]
        ).ids
        self.assertEqual(action["domain"], [("id", "in", pricelist_ids)])

    def test_fsm_order_purchase(self):
        fsm_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        self.assertEqual(fsm_order.purchase_count, 0)

        purchase = self.purchase_order_obj.create(
            {
                "partner_id": self.vendor.id,
                "fsm_order_id": fsm_order.id,
            }
        )
        self.assertEqual(fsm_order.purchase_count, 1)
        self.assertEqual(purchase.fsm_order_id, fsm_order)

        action = fsm_order.action_view_purchases()
        self.assertEqual(action["res_id"], purchase.id)
        self.assertEqual(action["context"].get("default_fsm_order_id"), fsm_order.id)

        po_action = purchase.action_view_fsm_order()
        self.assertEqual(po_action["res_id"], fsm_order.id)
        self.assertEqual(po_action["res_model"], "fsm.order")
