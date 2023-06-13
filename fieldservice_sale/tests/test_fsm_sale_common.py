# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale.tests.common import TestSaleCommonBase


class TestFSMSale(TestSaleCommonBase):
    @classmethod
    def setUpClass(cls):
        super(TestFSMSale, cls).setUpClass()

    @classmethod
    def setUpFSMTemplates(cls):
        # Create some templates to use on the FSM products
        FSMTemplate = cls.env["fsm.template"]

        # Template 1
        cls.fsm_template_1 = FSMTemplate.create(
            {
                "name": "Test FSM Template #1",
                "instructions": "These are the instructions for Template #1",
                "duration": 2.25,
            }
        )
        # Template 2
        cls.fsm_template_2 = FSMTemplate.create(
            {
                "name": "Test FSM Template #2",
                "instructions": "Template #2 requires a lot of work",
                "duration": 4.5,
            }
        )
        # Template 3
        cls.fsm_template_3 = FSMTemplate.create(
            {
                "name": "Test FSM Template #3",
                "instructions": "Complete the steps outlined for Template #3",
                "duration": 0.75,
            }
        )
        # Template 4
        cls.fsm_template_4 = FSMTemplate.create(
            {
                "name": "Test FSM Template #4",
                "instructions": "These notes apply to Template #4",
                "duration": 0.75,
            }
        )

    @classmethod
    def setUpFSMProducts(cls):
        cls.setUpFSMTemplates()
        # Product 1 that creates one FSM Order per SO
        cls.fsm_per_order_1 = cls.env["product.product"].create(
            {
                "name": "FSM Order per Sale Order #1",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 85.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "sale",
                "fsm_order_template_id": cls.fsm_template_1.id,
            }
        )

        # Product 2 that creates one FSM Order per SO
        cls.fsm_per_order_2 = cls.env["product.product"].create(
            {
                "name": "FSM Order per Sale Order #2",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 125.0,
                "list_price": 140.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "sale",
                "fsm_order_template_id": cls.fsm_template_2.id,
            }
        )
        # Product 1 that creates one FSM Order per SO Line
        cls.fsm_per_line_1 = cls.env["product.product"].create(
            {
                "name": "FSM Order per SO Line #1",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 75.0,
                "list_price": 80.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "delivery",
                "field_service_tracking": "line",
                "fsm_order_template_id": cls.fsm_template_3.id,
            }
        )
        # Product 2 that creates one FSM Order per SO Line
        cls.fsm_per_line_2 = cls.env["product.product"].create(
            {
                "name": "FSM Order per SO Line #2",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 75.0,
                "list_price": 80.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "delivery",
                "field_service_tracking": "line",
                "fsm_order_template_id": cls.fsm_template_4.id,
            }
        )
        # Normal Product
        cls.product_line = cls.env["product.template"].create(
            {
                "name": "FSM Order per SO Line #2",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 75.0,
                "list_price": 80.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "delivery",
                "field_service_tracking": "no",
                "fsm_order_template_id": cls.fsm_template_4.id,
            }
        )
        cls.product_line._onchange_field_service_tracking()
