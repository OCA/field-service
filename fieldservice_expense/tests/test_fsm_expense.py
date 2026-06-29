# Copyright (C) 2024 Open Source Integrators (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFieldserviceExpense(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.expense_user = cls.env["res.users"].create(
            {
                "name": "Expense User",
                "login": "fieldservice_expense_user",
                "group_ids": [
                    (6, 0, [cls.env.ref("hr_expense.group_hr_expense_user").id])
                ],
            }
        )
        cls.expense_employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Employee",
                "user_id": cls.expense_user.id,
                "work_contact_id": cls.expense_user.partner_id.id,
            }
        )
        cls.test_order = cls.env["fsm.order"].create(
            {"location_id": cls.test_location.id}
        )
        cls.expense_product = cls.env.ref("hr_expense.product_product_no_cost")

    def _create_expense(self, name, amount=100):
        return self.env["hr.expense"].create(
            {
                "name": name,
                "employee_id": self.expense_employee.id,
                "product_id": self.expense_product.id,
                "total_amount_currency": amount,
                "fsm_order_id": self.test_order.id,
            }
        )

    def test_expense_fsm_order_link(self):
        expense = self._create_expense("Travel")
        self.assertEqual(self.test_order.expense_count, 1)
        self.assertIn(expense, self.test_order.expense_ids)

        action = self.test_order.action_view_expenses()
        self.assertEqual(action["res_id"], expense.id)

        action_order = expense.action_view_order()
        self.assertEqual(action_order["res_id"], self.test_order.id)

    def test_action_view_expenses_multiple(self):
        self._create_expense("Expense 0", 50)
        self._create_expense("Expense 1", 50)
        action = self.test_order.action_view_expenses()
        self.assertEqual(action["domain"], [("fsm_order_id", "=", self.test_order.id)])
        self.assertEqual(self.test_order.expense_count, 2)

    def test_compute_expense_count_without_expenses(self):
        order = self.env["fsm.order"].create({"location_id": self.test_location.id})
        self.assertEqual(order.expense_count, 0)
