# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.fieldservice_sale.tests.test_fsm_sale_order import TestFSMSale


class TestFSMSaleRecurring(TestFSMSale):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_location = cls.env.ref("fieldservice.test_location")

        # Setup products that when sold will create some FSM orders
        cls.setUpFSMProducts()
        cls.partner_customer_usd = cls.env["res.partner"].create(
            {
                "name": "partner_a",
                "company_id": False,
            }
        )
        cls.pricelist_usd = cls.env["product.pricelist"].search(
            [("currency_id.name", "=", "USD")], limit=1
        )

        SaleOrder = cls.env["sale.order"].with_context(tracking_disable=True)

        cls.sale_order_recur = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sale_order_recur2 = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        # Product that creates FSM Recurring Order
        cls.product_fsm_recur = cls.env["product.product"].create(
            {
                "name": "FSM Recurring Order Product",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.env.ref(
                    "fieldservice_recurring.recur_template_weekdays"
                ).id,
            }
        )
        cls.product_fsm_recur2 = cls.env["product.product"].create(
            {
                "name": "FSM Recurring Order Product Test",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.env.ref(
                    "fieldservice_recurring.recur_template_weekdays"
                ).id,
            }
        )
        cls.product_fsm = cls.env["product.product"].create(
            {
                "name": "FSM Order Product",
                "categ_id": cls.env.ref("product.product_category_3").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "no",
            }
        )
        cls.sale_line_recurring = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur.name,
                "product_id": cls.product_fsm_recur.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_fsm_recur.uom_id.id,
                "price_unit": cls.product_fsm_recur.list_price,
                "order_id": cls.sale_order_recur.id,
                "tax_id": False,
            }
        )
        cls.sale_line_recurring2 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur2.name,
                "product_id": cls.product_fsm_recur2.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_fsm_recur2.uom_id.id,
                "price_unit": cls.product_fsm_recur2.list_price,
                "order_id": cls.sale_order_recur2.id,
                "tax_id": False,
            }
        )
        cls.sale_line_recurring3 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur.name,
                "product_id": cls.product_fsm_recur.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_fsm_recur.uom_id.id,
                "price_unit": cls.product_fsm_recur.list_price,
                "order_id": cls.sale_order_recur2.id,
                "tax_id": False,
            }
        )
        cls.sale_line_recurring4 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm.name,
                "product_id": cls.product_fsm.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_fsm.uom_id.id,
                "price_unit": cls.product_fsm.list_price,
                "order_id": cls.sale_order.id,
                "tax_id": False,
            }
        )

    def test_fsm_sale_order_recurring(self):
        """Test the flow for a Sale Order that will generate
        FSM Recurring Orders.
        """
        sol_recur = self.sale_line_recurring
        # Confirm the sale order that was setup
        self.sale_order_recur.action_confirm()
        self.sale_order_recur2.action_confirm()
        self.sale_order.action_confirm()

        # FSM Recurring Order linked to Sale Order Line
        count_recurring = self.env["fsm.recurring"].search_count(
            [("id", "=", sol_recur.fsm_recurring_id.id)]
        )
        self.assertEqual(
            count_recurring,
            1,
            """FSM Sale Recurring: Recurring Order should be linked to the
               Sale Order Line""",
        )
        sol_recur.fsm_recurring_id.action_view_sales()
        self.product_fsm.product_tmpl_id._onchange_field_service_tracking()
        self.product_fsm_recur.product_tmpl_id._onchange_field_service_tracking()
        self.sale_order_recur.action_view_fsm_recurring()
        self.sale_order_recur2.action_view_fsm_recurring()
        self.sale_order.action_view_fsm_recurring()
        # FSM Recurring Order linked to Sale Order
        self.assertEqual(
            len(self.sale_order_recur.fsm_recurring_ids.ids),
            1,
            """FSM Sale Recurring: Sale Order should create
               1 FSM Recurring Order""",
        )
