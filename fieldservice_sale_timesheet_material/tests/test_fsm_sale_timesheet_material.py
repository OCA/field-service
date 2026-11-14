# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestFSMSaleTimesheetMaterial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "FSM Customer"})
        # The time is recorded as timesheets of the order's project, which the
        # orders generated from the sale order get from their team.
        cls.project = cls.env["project.project"].create({"name": "Field Service"})
        cls.team = cls.env["fsm.team"].create(
            {"name": "FSM Team", "project_id": cls.project.id}
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "FSM Location",
                "partner_id": cls.customer.id,
                "owner_id": cls.customer.id,
                "team_id": cls.team.id,
            }
        )
        if not cls.env.user.employee_id:
            # timesheets are recorded by an employee
            cls.env["hr.employee"].create(
                {"name": "Technician", "user_id": cls.env.user.id}
            )
        cls.time_product = cls.env["product.product"].create(
            {
                "name": "Labor",
                "type": "service",
                "invoice_policy": "order",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.material = cls.env["product.product"].create(
            {"name": "Spare Part", "type": "consu"}
        )
        # A "per sale order" tracking product makes the sale order generate a
        # field service order on confirmation.
        cls.service = cls.env["product.product"].create(
            {
                "name": "Call-out fee",
                "type": "service",
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

    def _add_timesheet(self, hours, uom=None):
        vals = {
            "name": "Work done",
            "fsm_order_id": self.order.id,
            "project_id": self.order.project_id.id,
            "product_id": self.time_product.id,
            "unit_amount": hours,
        }
        if uom:
            vals["product_uom_id"] = uom.id
        return self.env["account.analytic.line"].create(vals)

    def test_order_project_from_team(self):
        # The order generated from the sale order has no project of its own:
        # it gets the one of its team
        self.assertEqual(self.order.team_id, self.team)
        self.assertEqual(self.order.project_id, self.project)

    def test_order_keeps_its_project(self):
        other_project = self.env["project.project"].create({"name": "Other"})
        order = self.env["fsm.order"].create(
            {"location_id": self.location.id, "project_id": other_project.id}
        )
        self.assertEqual(order.project_id, other_project)

    def test_timesheet_from_form(self):
        # Time recorded from the order form is a timesheet of the order's
        # project
        with Form(self.order) as order_form:
            with order_form.timesheet_ids.new() as line:
                line.name = "Travel"
                line.product_id = self.time_product
                line.unit_amount = 1.0
        self.assertEqual(self.order.timesheet_ids.name, "Travel")
        self.assertEqual(self.order.timesheet_ids.project_id, self.project)

    def _add_consumed_move(self, qty, uom=None):
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
                "product_uom": (uom or self.material.uom_id).id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "fsm_order_id": self.order.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        move.quantity = qty
        move.state = "done"
        return move

    def _add_returned_move(self, qty, uom=None):
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
                "product_uom": (uom or self.material.uom_id).id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "fsm_order_id": self.order.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        move.quantity = qty
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
                "project_id": order.project_id.id,
                "product_id": self.time_product.id,
                "unit_amount": 1.0,
            }
        )

        order.action_create_sale_lines()

        self.assertFalse(order.sale_id)
        self.assertFalse(order.timesheet_ids.mapped("fsm_sale_line_id"))

    def test_timesheet_uom_conversion(self):
        # A timesheet recorded in days is billed in the product's UoM (hours)
        day = self.env.ref("uom.product_uom_day")
        self._add_timesheet(1.0, uom=day)
        self.order.action_create_sale_lines()
        expected = day._compute_quantity(1.0, self.time_product.uom_id)
        self.assertEqual(self._time_lines().product_uom_qty, expected)
        self.assertEqual(self._time_lines().qty_delivered, expected)

    def test_material_uom_conversion(self):
        # A move done in dozens is billed in the product's UoM (units)
        self._add_consumed_move(1.0, uom=self.env.ref("uom.product_uom_dozen"))
        self.order.action_create_sale_lines()
        self.assertEqual(self._material_lines().product_uom_qty, 12.0)
        self.assertEqual(self._material_lines().product_uom, self.material.uom_id)

    def test_return_lowers_billed_quantity(self):
        # 4 consumed and 1 returned: only the net 3 are billed, and both
        # moves are marked as billed on the same line
        self._add_consumed_move(4.0)
        self._add_returned_move(1.0)
        self.order.action_create_sale_lines()
        material_lines = self._material_lines()
        self.assertEqual(len(material_lines), 1)
        self.assertEqual(material_lines.product_uom_qty, 3.0)
        self.assertEqual(material_lines.qty_delivered, 3.0)
        self.assertEqual(self.order.move_ids.fsm_sale_line_id, material_lines)

    def test_zero_quantity_skipped(self):
        # Nothing to bill: no time recorded and everything consumed came back
        self._add_timesheet(0.0)
        self._add_consumed_move(2.0)
        self._add_returned_move(2.0)
        self.order.action_create_sale_lines()
        self.assertFalse(self._time_lines())
        self.assertFalse(self._material_lines())
        self.assertFalse(self.order.timesheet_ids.fsm_sale_line_id)
        self.assertFalse(self.order.move_ids.fsm_sale_line_id)

    def test_skip_moves_already_on_sale_line(self):
        # A delivery that already belongs to a sale order line stays there and
        # is not billed a second time
        move = self._add_consumed_move(2.0)
        sold_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale.id,
                "product_id": self.material.id,
                "product_uom_qty": 2.0,
            }
        )
        move.sale_line_id = sold_line
        self.order.action_create_sale_lines()
        self.assertEqual(self._material_lines(), sold_line)
        self.assertEqual(move.sale_line_id, sold_line)
        self.assertFalse(move.fsm_sale_line_id)

    def test_skip_timesheets_billed_by_sale_line(self):
        # Time recorded on a billable project, whose sale order item is
        # invoiced based on timesheets, is already delivered on that item by
        # sale_timesheet: it is not added a second time
        hour = self.env.ref("uom.product_uom_hour")
        ts_product = self.env["product.product"].create(
            {
                "name": "Assistance",
                "type": "service",
                "invoice_policy": "delivery",
                "service_type": "timesheet",
                "uom_id": hour.id,
                "uom_po_id": hour.id,
            }
        )
        ts_sale_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale.id,
                "product_id": ts_product.id,
                "product_uom_qty": 10.0,
            }
        )
        project = self.env["project.project"].create(
            {
                "name": "Billable project",
                "allow_billable": True,
                "partner_id": self.customer.id,
            }
        )
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "fsm_order_id": self.order.id,
                "project_id": project.id,
                "employee_id": self.env["hr.employee"].create({"name": "Tech"}).id,
                "product_id": self.time_product.id,
                "unit_amount": 2.0,
                "so_line": ts_sale_line.id,
            }
        )
        self.assertEqual(ts_sale_line.qty_delivered, 2.0)
        self.order.action_create_sale_lines()
        self.assertFalse(self._time_lines())
        self.assertFalse(timesheet.fsm_sale_line_id)
        self.assertEqual(ts_sale_line.qty_delivered, 2.0)

    def test_time_product_with_computed_delivery_refused(self):
        # The delivered quantity of a time line is set from the recorded hours:
        # a Time Type product whose sale order item computes it (here based on
        # timesheets) would overwrite it, so the action refuses it
        self.time_product.write(
            {"service_type": "timesheet", "invoice_policy": "delivery"}
        )
        self._add_timesheet(3.0)
        with self.assertRaises(UserError):
            self.order.action_create_sale_lines()

    def test_prepaid_time_product(self):
        # A "Prepaid/Fixed Price" Time Type product is timesheet-based with
        # sale_timesheet, but its line invoices the ordered quantity, which is
        # the recorded hours: the delivered quantity does not matter
        self.time_product.service_policy = "ordered_prepaid"
        self.assertEqual(self.time_product.service_type, "timesheet")
        self._add_timesheet(3.0)
        self.order.action_create_sale_lines()
        time_line = self._time_lines()
        self.assertEqual(time_line.qty_delivered_method, "timesheet")
        self.assertEqual(time_line.product_uom_qty, 3.0)
        self.assertEqual(time_line.qty_to_invoice, 3.0)

    def test_salesman_bills_work_of_other_users(self):
        # The salesperson adding the work to the sale order bills the time
        # recorded by the technicians and the materials they used, even if the
        # record rules do not let them read those records
        salesman = new_test_user(
            self.env,
            login="fsm_salesman",
            groups="base.group_user,sales_team.group_sale_salesman,"
            "fieldservice.group_fsm_user",
        )
        self.sale.user_id = salesman
        timesheet = self._add_timesheet(3.0)
        move = self._add_consumed_move(2.0)
        self.order.with_user(salesman).action_create_sale_lines()
        self.assertEqual(self._time_lines().product_uom_qty, 3.0)
        self.assertEqual(self._material_lines().product_uom_qty, 2.0)
        self.assertEqual(timesheet.fsm_sale_line_id, self._time_lines())
        self.assertEqual(move.fsm_sale_line_id, self._material_lines())
