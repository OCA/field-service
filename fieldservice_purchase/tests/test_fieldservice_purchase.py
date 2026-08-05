# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo.tests import Form


class TestFieldServicePurchase(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.product_supplierinfo_obj = self.env["product.supplierinfo"]
        self.fsm_person_obj = self.env["fsm.person"]
        self.partner = self.env["res.partner"].create({"name": "Test Vendor"})
        self.location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "owner_id": self.env["res.partner"].create({"name": "Owner"}).id,
            }
        )

    def test_fieldservice_purchase(self):
        fsm_person = self.fsm_person_obj.create({"name": "Test FSM Person"})

        # Test with 1 records Vendor Pricelist
        product_supplierinfo_vals = {
            "partner_id": fsm_person.partner_id.id,
            "min_qty": 1.0,
            "price": 100,
        }
        self.product_supplierinfo_obj.create(product_supplierinfo_vals)

        fsm_person._compute_pricelist_count()
        self.assertEqual(
            fsm_person.pricelist_count, 1, "Wrong no of vendors pricelist!"
        )
        fsm_person.action_view_pricelists()

        # Test with 2 records Vendor Pricelist
        product_supplierinfo_vals = {
            "partner_id": fsm_person.partner_id.id,
            "min_qty": 2.0,
            "price": 200,
        }
        self.product_supplierinfo_obj.create(product_supplierinfo_vals)
        fsm_person._compute_pricelist_count()
        self.assertEqual(
            fsm_person.pricelist_count, 2, "Wrong no of vendors pricelist!"
        )
        fsm_person.action_view_pricelists()
        self.assertIsNone(self.fsm_person_obj.browse().action_view_pricelists())

    def test_fsm_order_purchase_link(self):
        fsm_order = self.env["fsm.order"].create({"location_id": self.location.id})
        purchase = self.env["purchase.order"].create({"partner_id": self.partner.id})
        self.assertEqual(fsm_order.purchase_count, 0)
        self.assertEqual(purchase.fsm_order_count, 0)

        fsm_order.purchase_ids = [(4, purchase.id)]
        self.assertEqual(fsm_order.purchase_count, 1)
        self.assertEqual(purchase.fsm_order_count, 1)

        action = fsm_order.action_view_purchases()
        self.assertEqual(action["domain"], [("id", "in", [purchase.id])])
        action = purchase.action_view_fsm_orders()
        self.assertEqual(action["domain"], [("id", "in", [fsm_order.id])])

    def test_fsm_order_purchase_link_from_ui(self):
        location = self.location
        partner = self.partner
        fsm_order = self.env["fsm.order"].create({"location_id": location.id})
        purchase = self.env["purchase.order"].create({"partner_id": partner.id})

        with Form(fsm_order) as order_form:
            order_form.purchase_ids.add(purchase)
        self.assertEqual(purchase.fsm_order_ids, fsm_order)

        other_order = self.env["fsm.order"].create({"location_id": location.id})
        with Form(purchase) as purchase_form:
            purchase_form.fsm_order_ids.add(other_order)
        self.assertEqual(other_order.purchase_ids, purchase)

        action = fsm_order.action_view_purchases()
        new_purchase = (
            self.env["purchase.order"]
            .with_context(**action["context"])
            .create({"partner_id": partner.id})
        )
        self.assertEqual(new_purchase.fsm_order_ids, fsm_order)

        action = purchase.action_view_fsm_orders()
        new_order = (
            self.env["fsm.order"]
            .with_context(**action["context"])
            .create({"location_id": location.id})
        )
        self.assertEqual(new_order.purchase_ids, purchase)
        self.assertEqual(purchase.fsm_order_count, 3)
