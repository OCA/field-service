# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError

from .test_fsm_sale_common import TestFSMSale


class TestFSMSaleOrder(TestFSMSale):
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
        cls.sale_order_wo_sol = SaleOrder.create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "pricelist_id": cls.pricelist_usd.id,
            }
        )
        cls.sale_order_sol = SaleOrder.create(
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
                "product_uom": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order.id,
                "tax_id": False,
            }
        )
        # cls.sol_service_per_order._compute_product_updatable()
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
                "product_uom": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order_1.id,
                "tax_id": False,
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
                "product_uom": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_2.id,
                "tax_id": False,
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
                "product_uom": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_3.id,
                "tax_id": False,
            }
        )
        cls.sol_service_per_line_3 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_2.name,
                "product_id": cls.fsm_per_line_2.id,
                "product_uom_qty": 1,
                "product_uom": cls.fsm_per_line_2.uom_id.id,
                "price_unit": cls.fsm_per_line_2.list_price,
                "order_id": cls.sale_order_3.id,
                "tax_id": False,
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
                "product_uom": cls.fsm_per_line_1.uom_id.id,
                "price_unit": cls.fsm_per_line_1.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_id": False,
            }
        )
        cls.sol_service_per_line_5 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_line_2.name,
                "product_id": cls.fsm_per_line_2.id,
                "product_uom_qty": 1,
                "product_uom": cls.fsm_per_line_2.uom_id.id,
                "price_unit": cls.fsm_per_line_2.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_id": False,
            }
        )
        cls.sol_service_per_order_2 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_1.name,
                "product_id": cls.fsm_per_order_1.id,
                "product_uom_qty": 1,
                "product_uom": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_id": False,
            }
        )
        cls.sol_service_per_order_3 = cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_2.name,
                "product_id": cls.fsm_per_order_2.id,
                "product_uom_qty": 1,
                "product_uom": cls.fsm_per_order_2.uom_id.id,
                "price_unit": cls.fsm_per_order_2.list_price,
                "order_id": cls.sale_order_4.id,
                "tax_id": False,
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
        """Test the sales order 0 flow from sale to invoice.
        - One FSM order linked to the Sale Order should be created.
        - One Invoice linked to the FSM Order should be created.
        """
        # Confirm the sale order
        sol = self.sol_service_per_order
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.sale_order.action_confirm()

        sol._compute_product_updatable()
        # 1 FSM order created

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
        - An Invoice linked to each FSM Order should be created.
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
        # 2 invoices created
        self.assertEqual(
            len(invoices.ids), 1, "FSM Sale: Sale Order 3 should create 1 invoices"
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
        - One Invoices should be created (One for each FSM Order).
        """
        sol1 = self.sol_service_per_line_4
        sol2 = self.sol_service_per_line_5
        # sol3 = self.sol_service_per_order_2
        # sol4 = self.sol_service_per_order_3

        # Confirm the sale order
        self.sale_order_4.action_confirm()
        # 3 orders created
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
        # 3 invoices created
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
                "product_uom": False,
                "price_unit": 0,
                "order_id": self.sale_order.id,
                "tax_id": False,
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
                "product_uom": False,
                "price_unit": 0,
                "order_id": self.sale_order.id,
                "tax_id": False,
            }
        )
        # confirm sale order: ValidationError shouldn't be raised
        self.sale_order.action_confirm()

    def test_sale_order_cancel(self):
        """Test that canceling a Sale Order cancels related FSM orders,
        and reconfirming creates a new FSM order while keeping old ones linked.
        """
        # Confirm the Sale Order
        self.sale_order_1.action_confirm()
        self.assertEqual(
            self.sale_order_1.state,
            "sale",
            "Sale Order should be confirmed (state=sale)",
        )
        self.assertEqual(
            len(self.sale_order_1.fsm_order_ids),
            1,
            "One FSM order should be created upon confirming the Sale Order",
        )

        fsm_order = self.sale_order_1.fsm_order_ids[0]

        # Cancel the Sale Order
        self.sale_order_1.with_context(
            disable_cancel_warning="disable_cancel_warning"
        ).action_cancel()
        self.assertEqual(
            self.sale_order_1.state,
            "cancel",
            "Sale Order should be canceled (state=cancel)",
        )

        self.assertTrue(
            fsm_order.is_closed,
            "FSM order should be marked as closed after Sale Order is canceled",
        )

        # Reconfirm the Sale Order
        self.sale_order_1.action_draft()
        self.sale_order_1.action_confirm()

        # Ensure that FSM orders are recomputed after reconfirmation
        self.sale_order_1._compute_fsm_order_ids()

        self.assertEqual(
            self.sale_order_1.state,
            "sale",
            "Sale Order should be re-confirmed (state=sale)",
        )
        self.assertEqual(
            len(self.sale_order_1.fsm_order_ids),
            2,
            "A new FSM order should be created upon reconfirming the "
            "Sale Order, while the old one remains linked.",
        )
