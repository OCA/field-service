# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.fieldservice_sale.tests.test_fsm_sale_order import TestFSMSale


class TestFSMSaleRecurring(TestFSMSale):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        registry = cls.env.registry
        has_auto = hasattr(registry, "_auto_install_template")
        if not has_auto:
            registry._auto_install_template = True
        try:
            cls.env["account.chart.template"].try_loading(
                "generic_coa", company=cls.env.company, install_demo=False
            )
        finally:
            if not has_auto:
                delattr(registry, "_auto_install_template")
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Location Partner"}
        )
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "owner_id": cls.test_loc_partner.id,
            }
        )

        freq = cls.env["fsm.frequency"].create(
            {
                "name": "Every Weekday",
                "interval": 1,
                "interval_type": "weekly",
                "use_byweekday": True,
                "mo": True,
                "tu": True,
                "we": True,
                "th": True,
                "fr": True,
            }
        )
        freq_set = cls.env["fsm.frequency.set"].create(
            {
                "name": "Weekdays Set",
                "fsm_frequency_ids": [(4, freq.id)],
            }
        )
        cls.recur_template = cls.env["fsm.recurring.template"].create(
            {
                "name": "Weekdays Template",
                "description": "Weekdays Template Description",
                "fsm_frequency_set_id": freq_set.id,
            }
        )

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
                "categ_id": cls.env.ref("product.product_category_services").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.recur_template.id,
            }
        )
        cls.product_fsm_recur2 = cls.env["product.product"].create(
            {
                "name": "FSM Recurring Order Product Test",
                "categ_id": cls.env.ref("product.product_category_services").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.recur_template.id,
            }
        )
        cls.product_fsm = cls.env["product.product"].create(
            {
                "name": "FSM Order Product",
                "categ_id": cls.env.ref("product.product_category_services").id,
                "standard_price": 425.0,
                "list_price": 500.0,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "no",
            }
        )
        cls.sale_line_recurring = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur.name,
                "product_id": cls.product_fsm_recur.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.product_fsm_recur.uom_id.id,
                "price_unit": cls.product_fsm_recur.list_price,
                "order_id": cls.sale_order_recur.id,
            }
        )
        cls.sale_line_recurring2 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur2.name,
                "product_id": cls.product_fsm_recur2.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.product_fsm_recur2.uom_id.id,
                "price_unit": cls.product_fsm_recur2.list_price,
                "order_id": cls.sale_order_recur2.id,
            }
        )
        cls.sale_line_recurring3 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm_recur.name,
                "product_id": cls.product_fsm_recur.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.product_fsm_recur.uom_id.id,
                "price_unit": cls.product_fsm_recur.list_price,
                "order_id": cls.sale_order_recur2.id,
            }
        )
        cls.sale_line_recurring4 = cls.env["sale.order.line"].create(
            {
                "name": cls.product_fsm.name,
                "product_id": cls.product_fsm.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.product_fsm.uom_id.id,
                "price_unit": cls.product_fsm.list_price,
                "order_id": cls.sale_order.id,
            }
        )

    def test_fsm_sale_order_recurring(self):
        """Test the flow for a Sale Order that will generate
        FSM Recurring Orders.
        """
        sol_recur = self.sale_line_recurring
        self.sale_order_recur.action_confirm()
        self.sale_order_recur2.action_confirm()
        self.sale_order.action_confirm()

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
        self.assertEqual(
            len(self.sale_order_recur.fsm_recurring_ids.ids),
            1,
            """FSM Sale Recurring: Sale Order should create
               1 FSM Recurring Order""",
        )

    def test_fsm_sale_order_recurring_invoicing(self):
        """Test the invoicing workflow for FSM Recurring Orders."""
        sol_recur = self.sale_line_recurring
        self.sale_order_recur.action_confirm()

        recurring = sol_recur.fsm_recurring_id
        self.assertTrue(recurring)

        vals = recurring._prepare_order_values()
        self.assertEqual(vals.get("sale_line_id"), sol_recur.id)

        stage_completed = self.env.ref("fieldservice.fsm_stage_completed")
        stage_completed.write({"is_invoiceable": True})

        fsm_order = self.env["fsm.order"].create(
            {
                "name": "Test Completed FSM Order",
                "fsm_recurring_id": recurring.id,
                "sale_line_id": sol_recur.id,
                "location_id": self.test_location.id,
                "stage_id": stage_completed.id,
            }
        )

        domain = sol_recur._get_invoiceable_fsm_order_domain()
        self.assertIn(("fsm_recurring_id", "=", recurring.id), domain)

        invoice = self.sale_order_recur._create_invoices()
        self.assertTrue(invoice)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == sol_recur.product_id
        )
        self.assertTrue(invoice_line)
        self.assertIn(fsm_order.id, invoice_line.fsm_order_ids.ids)

    def test_fsm_sale_order_recurring_invoicing_coverage(self):
        """Test negative/empty branches for full coverage on lines 82, 88, and 90."""
        sol_no_recur = self.sale_line_recurring4

        domain = sol_no_recur._get_invoiceable_fsm_order_domain()
        self.assertIsNotNone(domain)

        res_no_recur = sol_no_recur._prepare_invoice_line()
        self.assertNotIn("fsm_order_ids", res_no_recur)

        self.sale_order_recur2.action_confirm()
        sol_recur_no_orders = self.sale_line_recurring2

        res_recur_no_orders = sol_recur_no_orders._prepare_invoice_line()
        self.assertNotIn("fsm_order_ids", res_recur_no_orders)

    def test_onchange_field_service_tracking(self):
        """Test that changing field_service_tracking clears templates appropriately."""
        product_tmpl = self.product_fsm_recur.product_tmpl_id
        product_tmpl.field_service_tracking = "recurring"
        product_tmpl.fsm_recurring_template_id = self.recur_template

        product_tmpl.field_service_tracking = "no"
        product_tmpl._onchange_field_service_tracking()
        self.assertFalse(product_tmpl.fsm_recurring_template_id)
        self.assertFalse(product_tmpl.fsm_order_template_id)
