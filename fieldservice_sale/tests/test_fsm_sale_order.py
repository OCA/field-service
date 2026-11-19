# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from .test_fsm_sale_common import TestFSMSale


class TestFSMSaleOrder(TestFSMSale):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Location Partner"}
        )
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "owner_id": cls.test_loc_partner.id,
            }
        )
        cls.today = fields.Datetime.now()
        cls.dt1 = cls.today + datetime.timedelta(days=9)
        cls.dt2 = cls.today + datetime.timedelta(days=10)

        # Setup products that when sold will create some FSM orders
        cls.setUpFSMProducts()
        cls.partner_customer_usd = cls.env["res.partner"].create(
            {
                "name": "partner_a",
                "company_id": False,
            }
        )
        cls.pricelist_usd = cls.env["product.pricelist"].search(
            [("currency_id.name", "=", "USD"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        # Create some sale orders that will use the above products
        SaleOrder = cls.env["sale.order"].with_context(tracking_disable=True)
        # create a generic Sale Order with one product
        # set to create FSM service per sale order
        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sol_service_per_order = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_1.name,
                "product_id": cls.fsm_per_order_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order.id,
                "tax_ids": False,
            }
        )
        cls.sale_order_1 = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sol_service_per_order_1 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_1.name,
                "product_id": cls.fsm_per_order_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order_1.id,
                "tax_ids": False,
            }
        )
        # create a generic Sale Order with one product
        # set to create FSM service per sale order line
        cls.sale_order_2 = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sol_service_per_line_1 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_1.name,
                "product_id": cls.fsm_per_line_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_2.id,
                "tax_ids": False,
            }
        )
        # create a generic Sale Order with multiple products
        # set to create FSM service per sale order line
        cls.sale_order_3 = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sol_service_per_line_2 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_1.name,
                "product_id": cls.fsm_per_line_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_3.id,
                "tax_ids": False,
            }
        )
        cls.sol_service_per_line_3 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_2.name,
                "product_id": cls.fsm_per_line_2.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_line_2.uom_id.id,
                "price_unit": cls.fsm_per_line_2.list_price,
                "order_id": cls.sale_order_3.id,
                "tax_ids": False,
            }
        )
        # create a generic Sale Order with mixed products
        # 2 lines based on service per sale order line
        # 2 lines based on service per sale order
        cls.sale_order_4 = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sol_service_per_line_4 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_1.name,
                "product_id": cls.fsm_per_line_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_ids": False,
            }
        )
        cls.sol_service_per_line_5 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_2.name,
                "product_id": cls.fsm_per_line_2.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_line_2.uom_id.id,
                "price_unit": cls.fsm_per_line_2.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_ids": False,
            }
        )
        cls.sol_service_per_order_2 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_1.name,
                "product_id": cls.fsm_per_order_1.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_ids": False,
            }
        )
        cls.sol_service_per_order_3 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_2.name,
                "product_id": cls.fsm_per_order_2.id,
                "product_uom_qty": 1,
                "product_uom_id": cls.fsm_per_order_2.uom_id.id,
                "price_unit": cls.fsm_per_order_2.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_ids": False,
            }
        )

    def _isp_account_installed(self):
        """Checks if module is installed which will require more
        logic for the tests.
        :return Boolean indicating the installed status of the module
        """
        result = False
        isp_account_module = self.env["ir.module.module"].search(
            [("name", "=", "fieldservice_isp_account")]
        )
        if isp_account_module and isp_account_module.state == "installed":
            result = True
        return result

    def _fulfill_order(self, order):
        """Extra logic required to fulfill FSM order status and prevent
        validation error when attempting to complete the FSM order
        :return FSM Order with additional fields set
        """
        analytic_account = self.env.ref("analytic.analytic_administratif")
        self.test_location.analytic_account_id = analytic_account.id
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "timesheet_line",
                "unit_amount": 1,
                "account_id": analytic_account.id,
                "user_id": self.env.ref("base.partner_admin").id,
                "product_id": self.env.ref(
                    "fieldservice_isp_account.field_service_regular_time"
                ).id,
            }
        )
        order.write(
            {
                "employee_timesheet_ids": [(6, 0, timesheet.ids)],
            }
        )
        return order

    def test_sale_order_0(self):
        """Test that confirming a sale order with FSM products but no
        FSM location raises a ValidationError.
        """
        # sale_order has an FSM product line but no fsm_location_id set
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.sale_order.action_confirm()

    def test_sale_order_1(self):
        """Test the sales order 1 flow from sale to invoice.
        - One FSM order linked to the Sale Order should be created.
        - One Invoice linked to the FSM Order should be created.
        """
        # Confirm the sale order
        self.sale_order_1.action_confirm()
        # 1 FSM order created
        self.assertEqual(
            len(self.sale_order_1.fsm_order_ids.ids),
            1,
            "FSM Sale: Sale Order 1 should create 1 FSM Order",
        )
        FSM_Order = self.env["fsm.order"]
        fsm_order = FSM_Order.search(
            [("id", "=", self.sale_order_1.fsm_order_ids[0].id)]
        )
        # Sale Order linked to FSM order
        self.assertEqual(
            len(fsm_order.ids), 1, "FSM Sale: Sale Order not linked to FSM Order"
        )

        # Complete the FSM order
        if self._isp_account_installed():
            fsm_order = self._fulfill_order(fsm_order)
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()

        # Invoice the order
        invoice = self.sale_order_1._create_invoices()
        # 1 invoices created
        self.assertEqual(
            len(invoice.ids), 1, "FSM Sale: Sale Order 1 should create 1 invoice"
        )
        self.assertTrue(
            fsm_order in invoice.fsm_order_ids,
            "FSM Sale: Invoice should be linked to FSM Order",
        )

    def test_sale_order_2(self):
        """Test the sales order 2 flow from sale to invoice.
        - One FSM order linked to the Sale Order Line should be created.
        - The FSM Order should update qty_delivered when completed.
        - One Invoice linked to the FSM Order should be created.
        """
        sol = self.sol_service_per_line_1
        # Confirm the sale order
        self.sale_order_2.action_confirm()
        # 1 order created
        self.assertEqual(
            len(self.sale_order_2.fsm_order_ids.ids),
            1,
            "FSM Sale: Sale Order 2 should create 1 FSM Order",
        )
        FSM_Order = self.env["fsm.order"]

        fsm_order = FSM_Order.search([("id", "=", sol.fsm_order_id.id)])
        # SOL linked to FSM order
        self.assertTrue(
            sol.fsm_order_id.id == fsm_order.id,
            "FSM Sale: Sale Order 2 Line not linked to FSM Order",
        )

        # Complete the FSM order
        if self._isp_account_installed():
            fsm_order = self._fulfill_order(fsm_order)
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()
        # qty delivered should be updated
        self.assertTrue(
            sol.qty_delivered == sol.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )

        # Invoice the order
        invoice = self.sale_order_2._create_invoices()
        # 1 invoice created
        self.assertEqual(
            len(invoice.ids), 1, "FSM Sale: Sale Order 2 should create 1 invoice"
        )
        self.assertTrue(
            fsm_order in invoice.fsm_order_ids,
            "FSM Sale: Invoice should be linked to FSM Order",
        )

    def test_sale_order_3(self):
        """Test sale order 3 flow from sale to invoice.
        - An FSM order should be created for each Sale Order Line.
        - The FSM Order should update qty_delivered when completed.
        - One Invoice should be created, linked to both FSM Orders.
        """
        sol1 = self.sol_service_per_line_2
        sol2 = self.sol_service_per_line_3

        # Confirm the sale order
        self.sale_order_3.action_confirm()
        # 2 orders created and SOLs linked to FSM orders
        self.assertEqual(
            len(self.sale_order_3.fsm_order_ids.ids),
            2,
            "FSM Sale: Sale Order 3 should create 2 FSM Orders",
        )
        FSM_Order = self.env["fsm.order"]
        fsm_order_1 = FSM_Order.search([("id", "=", sol1.fsm_order_id.id)])
        self.assertTrue(
            sol1.fsm_order_id.id == fsm_order_1.id,
            "FSM Sale: Sale Order Line 2 not linked to FSM Order",
        )
        fsm_order_2 = FSM_Order.search([("id", "=", sol2.fsm_order_id.id)])
        self.assertTrue(
            sol2.fsm_order_id.id == fsm_order_2.id,
            "FSM Sale: Sale Order Line 3 not linked to FSM Order",
        )

        # Complete the FSM orders
        if self._isp_account_installed():
            fsm_order_1 = self._fulfill_order(fsm_order_1)
        fsm_order_1.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_1.action_complete()
        self.assertTrue(
            sol1.qty_delivered == sol1.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )
        if self._isp_account_installed():
            fsm_order_2 = self._fulfill_order(fsm_order_2)
        fsm_order_2.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_2.action_complete()
        self.assertTrue(
            sol2.qty_delivered == sol2.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )

        # Invoice the sale order
        invoices = self.sale_order_3._create_invoices()
        # 1 invoice created (one per sale order)
        self.assertEqual(
            len(invoices.ids), 1, "FSM Sale: Sale Order 3 should create 1 invoice"
        )
        inv_fsm_orders = FSM_Order
        for inv in invoices:
            inv_fsm_orders |= inv.fsm_order_ids
        self.assertTrue(
            fsm_order_1 in inv_fsm_orders,
            "FSM Sale: FSM Order 1 should be linked to invoice",
        )
        self.assertTrue(
            fsm_order_2 in inv_fsm_orders,
            "FSM Sale: FSM Order 2 should be linked to invoice",
        )

    def test_sale_order_4(self):
        """Test sale order 4 flow from sale to invoice.
        - Two FSM orders linked to the Sale Order Lines should be created.
        - One FSM order linked to the Sale Order should be created.
        - One Invoice should be created for the Sale Order.
        """
        sol1 = self.sol_service_per_line_4
        sol2 = self.sol_service_per_line_5

        # Confirm the sale order
        self.sale_order_4.action_confirm()
        # 3 FSM orders created (2 per-line + 1 per-order)
        self.assertEqual(
            len(self.sale_order_4.fsm_order_ids.ids),
            3,
            "FSM Sale: Sale Order 4 should create 3 FSM Orders",
        )
        FSM_Order = self.env["fsm.order"]
        fsm_order_1 = FSM_Order.search([("id", "=", sol1.fsm_order_id.id)])
        self.assertTrue(
            sol1.fsm_order_id.id == fsm_order_1.id,
            "FSM Sale: Sale Order Line not linked to FSM Order",
        )
        fsm_order_2 = FSM_Order.search([("id", "=", sol2.fsm_order_id.id)])
        self.assertTrue(
            sol2.fsm_order_id.id == fsm_order_2.id,
            "FSM Sale: Sale Order Line not linked to FSM Order",
        )
        fsm_order_3 = FSM_Order.search(
            [
                ("id", "in", self.sale_order_4.fsm_order_ids.ids),
                ("sale_line_id", "=", False),
            ]
        )
        self.assertEqual(
            len(fsm_order_3.ids), 1, "FSM Sale: FSM Order not linked to Sale Order"
        )

        # Complete the FSM order
        if self._isp_account_installed():
            fsm_order_1 = self._fulfill_order(fsm_order_1)
        fsm_order_1.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_1.action_complete()
        self.assertTrue(
            sol1.qty_delivered == sol1.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )
        if self._isp_account_installed():
            fsm_order_2 = self._fulfill_order(fsm_order_2)
        fsm_order_2.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_2.action_complete()
        self.assertTrue(
            sol2.qty_delivered == sol2.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )
        if self._isp_account_installed():
            fsm_order_3 = self._fulfill_order(fsm_order_3)
        fsm_order_3.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_3.action_complete()
        # qty_delivered does not update for FSM orders linked only to the sale

        # Invoice the sale order
        invoices = self.sale_order_4._create_invoices()
        # 1 invoice created (one per sale order)
        self.assertEqual(
            len(invoices.ids), 1, "FSM Sale: Sale Order 4 should create 1 invoice"
        )

    def test_sale_order_5(self):
        """Test ValidationError isn't raised if order line
        display_type in ("line_section", "line_note")
        """
        # remove normal order line with display_type=False
        self.sol_service_per_order.unlink()
        # add note as order line to sale order
        self.sol_note = self.env["sale.order.line"].create(
            {
                "name": "This is a note",
                "display_type": "line_note",
                "product_id": False,
                "product_uom_qty": 0,
                "product_uom_id": False,
                "price_unit": 0,
                "order_id": self.sale_order.id,
                "tax_ids": False,
            }
        )
        # confirm sale order: ValidationError shouldn't be raised
        self.sale_order.action_confirm()
        # set sale order to draft
        self.sale_order._action_cancel()
        self.sale_order.action_draft()
        # remove note order line
        self.sol_note.unlink()
        # add section as order line to sale order
        self.sol_section = self.env["sale.order.line"].create(
            {
                "name": "This is a section",
                "display_type": "line_section",
                "product_id": False,
                "product_uom_qty": 0,
                "product_uom_id": False,
                "price_unit": 0,
                "order_id": self.sale_order.id,
                "tax_ids": False,
            }
        )
        # confirm sale order: ValidationError shouldn't be raised
        self.sale_order.action_confirm()

    def test_sale_order_6(self):
        """Test sale order commitment date propagation to FSM orders"""
        # Confirm the sale order
        self.sale_order_3.action_confirm()
        # 2 orders created and SOLs linked to FSM orders
        self.assertEqual(
            len(self.sale_order_3.fsm_order_ids.ids),
            2,
            "FSM Sale: Sale Order 3 should create 2 FSM Orders",
        )
        self.sale_order_3.commitment_date = self.dt1
        self.assertEqual(
            self.sale_order_3.fsm_order_ids.mapped("scheduled_date_start")[0],
            self.sale_order_3.commitment_date,
            "FSM Sale: FSM Orders should have the same scheduled start date "
            "as the Sale Order commitment date",
        )
        # Changed commitment_date should be propagated to FSM Orders
        self.sale_order_3.write({"commitment_date": self.dt2})
        self.assertEqual(
            self.sale_order_3.fsm_order_ids.mapped("scheduled_date_start")[0],
            self.dt2,
            "FSM Sale: FSM Orders should have the new scheduled start date",
        )
        # Using the Form, empty commitment_date should fall back to expected_date
        with Form(self.sale_order_3) as order_form:
            order_form.commitment_date = False
            order_form.save()
        self.assertEqual(
            self.sale_order_3.fsm_order_ids.mapped("scheduled_date_start")[0],
            self.sale_order_3.expected_date,
            "FSM Sale: FSM Orders should have the same scheduled start date "
            "as the Sale Order expected date",
        )

    def test_product_onchange_field_service_tracking(self):
        """Setting field_service_tracking to 'no' clears the FSM template."""
        with Form(self.env["product.template"]) as product_form:
            product_form.name = "Onchange Test Product"
            product_form.type = "service"
            product_form.field_service_tracking = "sale"
            product_form.fsm_order_template_id = self.fsm_template_1
            # Switching back to 'no' must clear the template
            product_form.field_service_tracking = "no"
        product = product_form.save()
        self.assertFalse(
            product.fsm_order_template_id,
            "FSM Sale: fsm_order_template_id should be cleared when "
            "field_service_tracking is set to 'no'",
        )

    def test_sol_product_updatable(self):
        """A confirmed FSM service line is not product-updatable."""
        # Before confirmation the product can still be changed
        self.assertTrue(
            self.sol_service_per_order_1.product_updatable,
            "FSM Sale: draft SO line should be product-updatable",
        )
        self.sale_order_1.action_confirm()
        self.assertFalse(
            self.sol_service_per_order_1.product_updatable,
            "FSM Sale: confirmed FSM service line should not be product-updatable",
        )

    def test_sol_qty_delivered_method(self):
        """FSM 'per line' products use the field_service delivery method."""
        # field_service_tracking == "line" -> field_service method
        self.assertEqual(
            self.sol_service_per_line_1.qty_delivered_method,
            "field_service",
            "FSM Sale: per-line FSM product should use the "
            "field_service qty delivered method",
        )
        # field_service_tracking == "sale" -> not field_service
        self.assertNotEqual(
            self.sol_service_per_order_1.qty_delivered_method,
            "field_service",
            "FSM Sale: per-order FSM product should not use the "
            "field_service qty delivered method",
        )

    def test_sale_order_fsm_order_count(self):
        """fsm_order_count reflects the number of related FSM orders."""
        self.assertEqual(
            self.sale_order_3.fsm_order_count,
            0,
            "FSM Sale: unconfirmed SO should have no FSM orders",
        )
        self.sale_order_3.action_confirm()
        # fsm_order_count/ids are computed from a search on the fsm.order table,
        # which is not part of the compute's @api.depends. Invalidate the cache
        # to force a recompute, as a fresh read (page reload) would.
        self.sale_order_3.invalidate_recordset(["fsm_order_ids", "fsm_order_count"])
        self.assertEqual(
            self.sale_order_3.fsm_order_count,
            2,
            "FSM Sale: confirmed SO 3 should count its 2 FSM orders",
        )

    def test_action_view_sales_from_line(self):
        """action_view_sales targets the SO of the linked sale line."""
        self.sale_order_2.action_confirm()
        fsm_order = self.sol_service_per_line_1.fsm_order_id
        action = fsm_order.action_view_sales()
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(
            action["res_id"],
            self.sale_order_2.id,
            "FSM Sale: action should open the SO of the linked sale line",
        )
        self.assertFalse(action["context"]["create"])

    def test_action_view_sales_from_order(self):
        """action_view_sales falls back to sale_id when there is no line."""
        self.sale_order_1.action_confirm()
        # per-order FSM order has sale_id set but no sale_line_id
        fsm_order = self.sale_order_1.fsm_order_ids.filtered(
            lambda o: not o.sale_line_id
        )
        self.assertTrue(fsm_order, "FSM Sale: expected a per-order FSM order")
        action = fsm_order.action_view_sales()
        self.assertEqual(
            action["res_id"],
            self.sale_order_1.id,
            "FSM Sale: action should fall back to sale_id when no sale line",
        )

    def test_action_view_fsm_order_none(self):
        """action_view_fsm_order closes the window when there are no orders."""
        action = self.sale_order_1.action_view_fsm_order()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

    def test_action_view_fsm_order_single(self):
        """action_view_fsm_order opens the form for a single FSM order."""
        self.sale_order_1.action_confirm()
        action = self.sale_order_1.action_view_fsm_order()
        self.assertEqual(action["res_model"], "fsm.order")
        self.assertEqual(
            action["res_id"],
            self.sale_order_1.fsm_order_ids.id,
            "FSM Sale: single FSM order should open in form view",
        )
        # The single-order branch sets a form view and res_id (it does not set
        # a domain; the act_window default domain of False is left untouched).
        self.assertFalse(action["domain"])

    def test_action_view_fsm_order_multi(self):
        """action_view_fsm_order sets a domain for multiple FSM orders."""
        self.sale_order_3.action_confirm()
        action = self.sale_order_3.action_view_fsm_order()
        self.assertEqual(action["res_model"], "fsm.order")
        self.assertIn("domain", action)
        self.assertEqual(
            sorted(action["domain"][0][2]),
            sorted(self.sale_order_3.fsm_order_ids.ids),
            "FSM Sale: multiple FSM orders should be filtered by domain",
        )

    # -- sale.order.line specific coverage --------------------------------

    def test_sol_create_on_confirmed_order_generates_fsm(self):
        """Adding an FSM line to a confirmed SO generates its FSM order.

        Covers the create() override branch that calls
        _field_service_generation() when the new line's state is 'sale'.
        """
        # Confirm SO 2 first (it already has one per-line FSM order)
        self.sale_order_2.action_confirm()
        orders_before = self.sale_order_2.fsm_order_ids
        # Add a new per-line FSM product line to the already-confirmed order
        new_line = self.env["sale.order.line"].create(
            {
                "name": self.fsm_per_line_2.name,
                "product_id": self.fsm_per_line_2.id,
                "product_uom_qty": 1,
                "product_uom_id": self.fsm_per_line_2.uom_id.id,
                "price_unit": self.fsm_per_line_2.list_price,
                "order_id": self.sale_order_2.id,
                "tax_ids": False,
            }
        )
        # The new line is in state 'sale' (related to the confirmed order)
        self.assertEqual(new_line.state, "sale")
        # An FSM order was generated for the new line at create time
        self.assertTrue(
            new_line.fsm_order_id,
            "FSM Sale: creating a line on a confirmed SO should generate its FSM order",
        )
        self.sale_order_2.invalidate_recordset(["fsm_order_ids"])
        self.assertIn(
            new_line.fsm_order_id,
            self.sale_order_2.fsm_order_ids,
            "FSM Sale: newly generated FSM order should belong to the SO",
        )
        self.assertEqual(
            len(self.sale_order_2.fsm_order_ids),
            len(orders_before) + 1,
            "FSM Sale: exactly one new FSM order should be generated",
        )

    def test_sol_create_on_draft_order_no_generation(self):
        """Creating an FSM line on a draft SO does not generate an order.

        Covers the create() override branch where state != 'sale'.
        """
        line = self.sol_service_per_line_1  # belongs to draft sale_order_2
        self.assertNotEqual(line.state, "sale")
        self.assertFalse(
            line.fsm_order_id,
            "FSM Sale: no FSM order should exist for a draft SO line",
        )

    def test_sol_compute_qty_delivered_on_completion(self):
        """qty_delivered follows product_uom_qty once the FSM order is done.

        Covers _compute_qty_delivered: the field_service line whose FSM order
        reaches the completed stage gets qty_delivered set to the ordered qty.
        """
        sol = self.sol_service_per_line_1
        self.sale_order_2.action_confirm()
        fsm_order = sol.fsm_order_id
        # Not completed yet -> nothing delivered
        self.assertEqual(sol.qty_delivered, 0.0)
        # Complete the FSM order (sets stage to fsm_stage_completed)
        if self._isp_account_installed():
            fsm_order = self._fulfill_order(fsm_order)
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()
        sol.invalidate_recordset(["qty_delivered"])
        self.assertEqual(
            sol.qty_delivered,
            sol.product_uom_qty,
            "FSM Sale: completed FSM order should set qty_delivered to the "
            "ordered quantity",
        )

    def test_sol_invoiceable_fsm_order_domain_without_stage(self):
        """Domain has no stage clause when no stage is invoiceable.

        Covers _get_invoiceable_fsm_order_domain skipping the stage_id append.
        """
        # Ensure no stage is flagged invoiceable
        self.env["fsm.stage"].search([]).write({"is_invoiceable": False})
        self.sale_order_2.action_confirm()
        sol = self.sol_service_per_line_1
        domain = sol._get_invoiceable_fsm_order_domain()
        self.assertNotIn(
            "stage_id",
            [leaf[0] for leaf in domain if isinstance(leaf, (list, tuple))],
            "FSM Sale: domain should not filter by stage_id when no stage is "
            "invoiceable",
        )
        # The domain still resolves the line's FSM order
        self.assertIn(sol.fsm_order_id, sol._get_invoiceable_fsm_order())

    def test_sol_invoiceable_fsm_order_domain_with_stage(self):
        """Domain adds a stage_id clause when a stage is invoiceable.

        Covers the _get_invoiceable_fsm_order_domain stage_id append branch.
        """
        self.sale_order_2.action_confirm()
        sol = self.sol_service_per_line_1
        completed_stage = self.env.ref("fieldservice.fsm_stage_completed")
        completed_stage.is_invoiceable = True
        domain = sol._get_invoiceable_fsm_order_domain()
        stage_leaves = [
            leaf
            for leaf in domain
            if isinstance(leaf, (list, tuple)) and leaf[0] == "stage_id"
        ]
        self.assertEqual(
            len(stage_leaves),
            1,
            "FSM Sale: domain should filter by stage_id when a stage is invoiceable",
        )
        self.assertIn(completed_stage.id, stage_leaves[0][2])

    def test_sol_prepare_invoice_line_links_fsm_order(self):
        """_prepare_invoice_line attaches the invoiceable FSM order(s).

        Covers the fsm_order_id / fsm_orders branch of _prepare_invoice_line.
        """
        self.sale_order_2.action_confirm()
        sol = self.sol_service_per_line_1
        # Complete the FSM order so it is invoiceable
        fsm_order = sol.fsm_order_id
        if self._isp_account_installed():
            fsm_order = self._fulfill_order(fsm_order)
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()
        invoice = self.sale_order_2._create_invoices()
        self.assertIn(
            fsm_order,
            invoice.fsm_order_ids,
            "FSM Sale: invoice line should be linked to the FSM order",
        )

    def test_sol_prepare_invoice_line_no_fsm_order(self):
        """_prepare_invoice_line leaves non-FSM lines untouched.

        Covers the branch where the sale line has no fsm_order_id.
        """
        # Use the non-FSM product on a fresh confirmed order
        SaleOrder = self.env["sale.order"].with_context(tracking_disable=True)
        order = SaleOrder.create(
            {
                "partner_id": self.partner_customer_usd.id,
                "fsm_location_id": self.test_location.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "name": self.product_no_tracking.name,
                "product_id": self.product_no_tracking.product_variant_id.id,
                "product_uom_qty": 1,
                "product_uom_id": self.product_no_tracking.uom_id.id,
                "price_unit": self.product_no_tracking.list_price,
                "order_id": order.id,
                "tax_ids": False,
            }
        )
        order.action_confirm()
        self.assertFalse(
            line.fsm_order_id,
            "FSM Sale: non-tracked product should not create an FSM order",
        )
        vals = line._prepare_invoice_line()
        self.assertNotIn(
            "fsm_order_ids",
            vals,
            "FSM Sale: invoice line vals should not reference FSM orders for a "
            "non-tracked product",
        )
