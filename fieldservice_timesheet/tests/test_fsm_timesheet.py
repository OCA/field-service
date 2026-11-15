# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMTimesheet(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Order = cls.env["fsm.order"]
        cls.Timesheet = cls.env["account.analytic.line"]
        cls.project = cls.env["project.project"].create(
            {
                "name": "FSM Timesheet Project",
                "allow_timesheets": True,
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "FSM Timesheet Task",
                "project_id": cls.project.id,
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "FSM Timesheet Employee",
                "user_id": cls.env.user.id,
            }
        )
        cls.order = cls.Order.create(
            {
                "location_id": cls.test_location.id,
                "project_id": cls.project.id,
                "project_task_id": cls.task.id,
            }
        )

    def test_timesheet_linked_to_fsm_order(self):
        timesheet = self.Timesheet.create(
            {
                "name": "On-site work",
                "project_id": self.project.id,
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
                "fsm_order_id": self.order.id,
            }
        )
        self.assertIn(timesheet, self.order.timesheet_ids)
        self.assertEqual(timesheet.fsm_order_id, self.order)

    def test_timesheet_analysis_report_includes_fsm_order(self):
        self.Timesheet.create(
            {
                "name": "Analysis report work",
                "project_id": self.project.id,
                "task_id": self.task.id,
                "employee_id": self.employee.id,
                "unit_amount": 1.5,
                "fsm_order_id": self.order.id,
            }
        )
        report_lines = self.env["timesheets.analysis.report"].search(
            [("fsm_order_id", "=", self.order.id)]
        )
        self.assertTrue(report_lines)
        self.assertEqual(report_lines[0].fsm_order_id, self.order)
