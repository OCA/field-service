# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.fieldservice_sale.tests.test_fsm_sale_common import TestFSMSale


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
        cls.fsm_per_order_1 = cls.env["product.product"].create(
            {
                "name": "FSM Order per Sale Order #1",
                "categ_id": cls.env.ref("product.product_category_goods").id,
                "standard_price": 85.0,
                "list_price": 90.0,
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "invoice_policy": "order",
                "field_service_tracking": "sale",
                "fsm_order_template_id": cls.fsm_template_1.id,
            }
        )
        SaleOrder = cls.env["sale.order"].with_context(tracking_disable=True)
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

    def _isp_account_installed(self):  # pragma: no cover
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

    def _fulfill_order(self, order):  # pragma: no cover
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

    def test_sale_order_1(self):
        """Test the sales order 1 flow from sale to invoice.
        - One FSM order linked to the Sale Order should be created.
        - One Invoice linked to the FSM Order should be created.
        """
        self.sale_order_1.action_confirm()
        self.assertEqual(
            len(self.sale_order_1.fsm_order_ids.ids),
            1,
            "FSM Sale: Sale Order 1 should create 1 FSM Order",
        )
        FSM_Order = self.env["fsm.order"]
        fsm_order = FSM_Order.search(
            [("id", "=", self.sale_order_1.fsm_order_ids[0].id)]
        )
        self.assertEqual(
            len(fsm_order.ids), 1, "FSM Sale: Sale Order not linked to FSM Order"
        )
        self.assertTrue(
            self.sale_order_1.picking_ids,
            "FSM Sale: Sale Order 1 should create stock pickings",
        )
        for picking in self.sale_order_1.picking_ids:
            self.assertEqual(
                picking.fsm_order_id,
                fsm_order,
                "FSM Sale: Stock Picking should be linked to FSM Order",
            )
            for move in picking.move_ids:
                self.assertEqual(
                    move.fsm_order_id,
                    fsm_order,
                    "FSM Sale: Stock Move should be linked to FSM Order",
                )
        if self.sale_order_1.stock_reference_ids:
            self.assertTrue(
                set(self.sale_order_1.stock_reference_ids.ids).issubset(
                    set(fsm_order.reference_ids.ids)
                ),
                "FSM Sale: Stock References should be linked to FSM Order",
            )

        if self._isp_account_installed():  # pragma: no cover
            fsm_order = self._fulfill_order(fsm_order)  # pragma: no cover
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()
        invoice = self.sale_order_1._create_invoices()
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
        self.sale_order_2.action_confirm()
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

        if self._isp_account_installed():  # pragma: no cover
            fsm_order = self._fulfill_order(fsm_order)  # pragma: no cover
        fsm_order.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order.action_complete()
        self.assertTrue(
            sol.qty_delivered == sol.product_uom_qty,
            "FSM Sale: Sale Order Line qty delivered not equal to qty ordered",
        )

        invoice = self.sale_order_2._create_invoices()
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

        self.sale_order_3.action_confirm()
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

        if self._isp_account_installed():  # pragma: no cover
            fsm_order_1 = self._fulfill_order(fsm_order_1)  # pragma: no cover
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
        if self._isp_account_installed():  # pragma: no cover
            fsm_order_2 = self._fulfill_order(fsm_order_2)  # pragma: no cover
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

        invoices = self.sale_order_3._create_invoices()
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

        self.sale_order_4.action_confirm()
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
        if self._isp_account_installed():  # pragma: no cover
            fsm_order_1 = self._fulfill_order(fsm_order_1)  # pragma: no cover
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
        if self._isp_account_installed():  # pragma: no cover
            fsm_order_2 = self._fulfill_order(fsm_order_2)  # pragma: no cover
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
        if self._isp_account_installed():  # pragma: no cover
            fsm_order_3 = self._fulfill_order(fsm_order_3)  # pragma: no cover
        fsm_order_3.write(
            {
                "date_end": fields.Datetime.today(),
                "resolution": "Work completed",
            }
        )
        fsm_order_3.action_complete()
        invoices = self.sale_order_4._create_invoices()
        self.assertEqual(
            len(invoices.ids), 1, "FSM Sale: Sale Order 4 should create 1 invoice"
        )

    def test_prepare_fsm_values_methods(self):
        """Test helper methods prepare_fsm_values_for_stock_picking and
        prepare_fsm_values_for_stock_move."""
        fsm_order = self.env["fsm.order"].create(
            {
                "name": "Test FSM Order",
                "location_id": self.test_location.id,
            }
        )
        picking_vals = self.sale_order_1.prepare_fsm_values_for_stock_picking(fsm_order)
        move_vals = self.sale_order_1.prepare_fsm_values_for_stock_move(fsm_order)
        self.assertEqual(picking_vals, {"fsm_order_id": fsm_order.id})
        self.assertEqual(move_vals, {"fsm_order_id": fsm_order.id})
