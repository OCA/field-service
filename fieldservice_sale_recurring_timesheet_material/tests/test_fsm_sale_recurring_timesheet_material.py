# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestFSMSaleRecurringTimesheetMaterial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.customer = cls.env["res.partner"].create({"name": "FSM Customer"})
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "FSM Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "FSM Account", "plan_id": cls.analytic_plan.id}
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "FSM Location",
                "partner_id": cls.customer.id,
                "owner_id": cls.customer.id,
                "customer_id": cls.customer.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.time_product = cls.env["product.product"].create(
            {
                "name": "Labor",
                "detailed_type": "service",
                "invoice_policy": "order",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.material = cls.env["product.product"].create(
            {"name": "Spare Part", "detailed_type": "consu"}
        )
        # A recurring order is sold, and generates the field service orders
        # from its frequency rules.
        frequency = cls.env["fsm.frequency"].create(
            {"name": "Every day", "interval": 1, "interval_type": "daily"}
        )
        frequency_set = cls.env["fsm.frequency.set"].create(
            {
                "name": "Daily",
                "fsm_frequency_ids": [(6, 0, frequency.ids)],
                "schedule_days": 7,
            }
        )
        cls.recurring_template = cls.env["fsm.recurring.template"].create(
            {
                "name": "Daily maintenance",
                "fsm_frequency_set_id": frequency_set.id,
                "max_orders": 3,
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Maintenance contract",
                "detailed_type": "service",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.recurring_template.id,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "fsm_location_id": cls.location.id,
                "order_line": [
                    (0, 0, {"product_id": cls.service.id, "product_uom_qty": 1})
                ],
            }
        )
        cls.sale.action_confirm()
        cls.recurring = cls.sale.order_line.fsm_recurring_id
        cls.recurring.action_start()
        cls.order = cls.recurring.fsm_order_ids[0]

    def _add_timesheet(self, hours):
        return self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": self.order.id,
                "product_id": self.time_product.id,
                "unit_amount": hours,
            }
        )

    def _add_consumed_move(self, qty):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        out_type = warehouse.out_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": out_type.id,
                "location_id": out_type.default_location_src_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.material.name,
                "product_id": self.material.id,
                "product_uom": self.material.uom_id.id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "fsm_order_id": self.order.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        move.quantity_done = qty
        move.state = "done"
        return move

    def _sale_lines(self, product):
        return self.sale.order_line.filtered(lambda sol: sol.product_id == product)

    def test_orders_are_linked_to_the_sale_order_line(self):
        """The generated orders are sold through the sale order line."""
        self.assertEqual(len(self.recurring.fsm_order_ids), 3)
        for order in self.recurring.fsm_order_ids:
            self.assertFalse(order.sale_id)
            self.assertEqual(order.sale_line_id, self.sale.order_line)

    def test_create_sale_lines_timesheet_and_material(self):
        """Time and materials are added to the sale order that sold the
        recurring order, even though the field service order has no sale order
        of its own.
        """
        self._add_timesheet(3.0)
        self._add_timesheet(2.0)
        self._add_consumed_move(4.0)

        self.order.action_create_sale_lines()

        time_lines = self._sale_lines(self.time_product)
        self.assertEqual(len(time_lines), 1)
        self.assertEqual(time_lines.order_id, self.sale)
        self.assertEqual(time_lines.product_uom_qty, 5.0)
        self.assertEqual(time_lines.qty_delivered, 5.0)
        self.assertEqual(time_lines.fsm_order_id, self.order)

        material_lines = self._sale_lines(self.material)
        self.assertEqual(len(material_lines), 1)
        self.assertEqual(material_lines.order_id, self.sale)
        self.assertEqual(material_lines.product_uom_qty, 4.0)
        self.assertEqual(material_lines.fsm_order_id, self.order)

        self.assertTrue(all(self.order.timesheet_ids.mapped("fsm_sale_line_id")))
        self.assertTrue(all(self.order.move_ids.mapped("fsm_sale_line_id")))

    def test_idempotent(self):
        """Only work that has not been billed yet is added."""
        self._add_timesheet(3.0)
        self.order.action_create_sale_lines()
        self.assertEqual(len(self._sale_lines(self.time_product)), 1)

        self.order.action_create_sale_lines()
        self.assertEqual(len(self._sale_lines(self.time_product)), 1)

        self._add_timesheet(1.0)
        self.order.action_create_sale_lines()
        self.assertEqual(len(self._sale_lines(self.time_product)), 2)

    def test_each_order_bills_its_own_work(self):
        """Every order of the recurring order bills on the same sale order."""
        other_order = self.recurring.fsm_order_ids[1]
        self._add_timesheet(3.0)
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": other_order.id,
                "product_id": self.time_product.id,
                "unit_amount": 1.5,
            }
        )

        (self.order | other_order).action_create_sale_lines()

        time_lines = self._sale_lines(self.time_product)
        self.assertEqual(len(time_lines), 2)
        self.assertEqual(sum(time_lines.mapped("product_uom_qty")), 4.5)
        self.assertEqual(time_lines.mapped("fsm_order_id"), self.order | other_order)

    def test_order_without_sale_does_nothing(self):
        """An order sold neither by a sale order nor by a sale order line has
        nothing to bill.
        """
        order = self.env["fsm.order"].create({"location_id": self.location.id})
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": order.id,
                "product_id": self.time_product.id,
                "unit_amount": 1.0,
            }
        )

        order.action_create_sale_lines()

        self.assertFalse(order.timesheet_ids.mapped("fsm_sale_line_id"))

    def test_invoice_is_linked_to_the_order(self):
        """The invoice line billing the work of an order is linked to that
        order, although the order has no sale order of its own.
        """
        self._add_timesheet(3.0)
        self.order.action_create_sale_lines()

        invoice = self.sale._create_invoices()

        time_invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == self.time_product
        )
        self.assertEqual(len(time_invoice_line), 1)
        self.assertEqual(time_invoice_line.fsm_order_ids, self.order)
        self.assertEqual(self.order.invoice_ids, invoice)

    def test_recurring_action_create_sale_lines(self):
        """The recurring order's button bills the work of all its orders."""
        other_order = self.recurring.fsm_order_ids[1]
        self._add_timesheet(3.0)
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": other_order.id,
                "product_id": self.time_product.id,
                "unit_amount": 1.5,
            }
        )

        action = self.recurring.action_create_sale_lines()

        time_lines = self._sale_lines(self.time_product)
        self.assertEqual(len(time_lines), 2)
        self.assertEqual(time_lines.mapped("fsm_order_id"), self.order | other_order)
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(action["res_id"], self.sale.id)

        # nothing is billed twice
        self.recurring.action_create_sale_lines()
        self.assertEqual(len(self._sale_lines(self.time_product)), 2)
