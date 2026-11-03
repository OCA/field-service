# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestReportTimesheet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("fieldservice.group_fsm_user")
        cls.order = cls.env["fsm.order"].create(
            {"location_id": cls.env.ref("fieldservice.test_location").id}
        )
        cls.project = cls.env["project.project"].create({"name": "FSM Project"})
        cls.line = cls.env["account.analytic.line"].create(
            {
                "name": "Repair",
                "project_id": cls.project.id,
                "employee_id": cls.env.ref("hr.employee_admin").id,
                "fsm_order_id": cls.order.id,
                "unit_amount": 2,
            }
        )

    def test_report_timesheet_shows_fsm_order(self):
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("hr_timesheet.report_timesheet", self.line.ids)[0]
            .decode()
        )
        self.assertIn("Field Service Order", html)
        self.assertIn(self.order.name, html)
