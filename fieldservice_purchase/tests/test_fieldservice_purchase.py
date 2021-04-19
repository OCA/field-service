# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestFieldServicePurchase(common.TransactionCase):
    def setUp(self):
        super(TestFieldServicePurchase, self).setUp()

        self.product_supplierinfo_obj = self.env["product.supplierinfo"]
        self.fsm_person_obj = self.env["fsm.person"]

    def test_fieldservice_purchase(self):

        fsm_person = self.fsm_person_obj.create({"name": "Test FSM Person"})

        # Test with 1 records Vendor Pricelist
        product_supplierinfo_vals = {
            "name": fsm_person.partner_id.id,
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
            "name": fsm_person.partner_id.id,
            "min_qty": 2.0,
            "price": 200,
        }
        self.product_supplierinfo_obj.create(product_supplierinfo_vals)
        fsm_person._compute_pricelist_count()
        self.assertEqual(
            fsm_person.pricelist_count, 2, "Wrong no of vendors pricelist!"
        )
        fsm_person.action_view_pricelists()
