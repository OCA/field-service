# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMSaleTimesheetMaterial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        # A "per sale order" tracking product makes the sale order generate a
        # field service order on confirmation.
        cls.service = cls.env["product.product"].create(
            {
                "name": "Call-out fee",
                "detailed_type": "service",
                "field_service_tracking": "sale",
            }
        )
        # The field service order is generated from the confirmed sale order
        # (here holding a call-out fee); the recorded timesheets and consumed
        # materials are pushed back to that same order for invoicing.
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [
                    (0, 0, {"product_id": cls.service.id, "product_uom_qty": 1})
                ],
            }
        )
        cls.sale.action_confirm()
        cls.order = cls.sale.fsm_order_ids

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

    def _add_returned_move(self, qty):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        in_type = warehouse.in_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": in_type.id,
                "location_id": self.env.ref("stock.stock_location_customers").id,
                "location_dest_id": in_type.default_location_dest_id.id,
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

    def _time_lines(self):
        return self.sale.order_line.filtered(
            lambda sol: sol.product_id == self.time_product
        )

    def _material_lines(self):
        return self.sale.order_line.filtered(
            lambda sol: sol.product_id == self.material
        )

    def test_create_sale_lines_timesheet_and_material(self):
        self._add_timesheet(3.0)
        self._add_timesheet(2.0)
        self._add_consumed_move(4.0)

        self.order.action_create_sale_lines()

        # the order's existing sale order is reused, never recreated
        self.assertEqual(self.order.sale_id, self.sale)

        time_lines = self._time_lines()
        self.assertEqual(len(time_lines), 1)
        self.assertEqual(time_lines.product_uom_qty, 5.0)
        self.assertEqual(time_lines.qty_delivered, 5.0)
        self.assertEqual(time_lines.fsm_order_id, self.order)

        material_lines = self._material_lines()
        self.assertEqual(len(material_lines), 1)
        self.assertEqual(material_lines.product_uom_qty, 4.0)
        # the consumed move is linked to the line through the standard
        # sale_line_id, so the delivered quantity is computed from it natively
        self.assertEqual(self.order.move_ids.sale_line_id, material_lines)
        self.assertEqual(material_lines.qty_delivered, 4.0)
        # no duplicate delivery is generated for the already-consumed goods,
        # even though the line is added to a confirmed order
        self.assertFalse(
            self.sale.picking_ids,
            "no delivery should be created for already-consumed materials",
        )

        # all timesheets / moves are now linked to a sale order line
        self.assertTrue(all(self.order.timesheet_ids.mapped("fsm_sale_line_id")))
        self.assertTrue(all(self.order.move_ids.mapped("fsm_sale_line_id")))

    def test_idempotent(self):
        self._add_timesheet(3.0)
        self.order.action_create_sale_lines()
        self.assertEqual(len(self._time_lines()), 1)

        # second call adds nothing for already-billed work
        self.order.action_create_sale_lines()
        self.assertEqual(len(self._time_lines()), 1)

        # new work is added to the same sale order
        self._add_timesheet(1.0)
        self.order.action_create_sale_lines()
        self.assertEqual(len(self._time_lines()), 2)

    def test_report_material_lines_lists_used_and_returned(self):
        # 4 consumed and 1 returned are shown as two separate rows, not netted
        self._add_consumed_move(4.0)
        self._add_returned_move(1.0)

        lines = self.order._report_material_lines()
        self.assertEqual(len(lines), 2)
        # used row comes first, returned row second
        used, returned = lines
        self.assertEqual(used["product"], self.material)
        self.assertEqual(used["direction"], "out")
        self.assertEqual(used["qty"], 4.0)
        self.assertEqual(used["uom"], self.material.uom_id)
        self.assertEqual(returned["direction"], "in")
        self.assertEqual(returned["qty"], 1.0)

    def test_report_material_lines_empty_without_moves(self):
        self.assertFalse(self.order._report_material_lines())

    def test_report_renders_time_and_materials(self):
        self._add_timesheet(3.0)
        self._add_timesheet(1.5)
        self._add_consumed_move(4.0)
        self._add_returned_move(1.0)

        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("fieldservice.report_fsm_order", self.order.ids)[0]
            .decode()
        )

        self.assertIn("Time Spent", html)
        self.assertIn("Materials", html)
        # the timesheet total (4.5 h) is rendered as a float_time duration
        self.assertIn("04:30", html)
        # both directions are shown for the consumed material
        self.assertIn(self.material.name, html)
        self.assertIn("Used", html)
        self.assertIn("Returned", html)

    def test_without_sale_order_does_nothing(self):
        # An order not generated from a sale order has nothing to push to: the
        # action is a no-op and never creates a sale order (the button is also
        # hidden for such orders).
        order = self.env["fsm.order"].create(
            {
                "location_id": self.location.id,
                "date_start": fields.Datetime.today(),
                "date_end": fields.Datetime.today() + timedelta(hours=2),
                "request_early": fields.Datetime.today(),
            }
        )
        self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": order.id,
                "product_id": self.time_product.id,
                "unit_amount": 1.0,
            }
        )

        order.action_create_sale_lines()

        self.assertFalse(order.sale_id)
        self.assertFalse(order.timesheet_ids.mapped("fsm_sale_line_id"))
