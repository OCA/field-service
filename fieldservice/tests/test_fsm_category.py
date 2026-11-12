# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from . import test_fsm_order


class TestFsmCategory(test_fsm_order.TestFSMOrder):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fsm_category = cls.env["fsm.category"]
        cls.fsm_category_a = fsm_category.create({"name": "Category A"})
        cls.fsm_category_b = fsm_category.create(
            {"name": "Category B", "parent_id": cls.fsm_category_a.id}
        )
        cls.fsm_category_c = fsm_category.create(
            {"name": "Category C", "parent_id": cls.fsm_category_b.id}
        )

    def test_fsm_order_category(self):
        self.assertEqual(self.fsm_category_a.full_name, self.fsm_category_a.name)
        self.assertEqual(
            self.fsm_category_b.full_name,
            f"{self.fsm_category_a.name} / {self.fsm_category_b.name}",
        )

    def test_fsm_category_recursion(self):
        self.assertFalse(self.fsm_category_c._has_cycle())
        with self.assertRaises(UserError):
            self.fsm_category_a.write({"parent_id": self.fsm_category_c.id})

    def test_fsm_category_self_parent(self):
        with self.assertRaises(UserError):
            self.fsm_category_a.write({"parent_id": self.fsm_category_a.id})

    def test_fsm_category_child_created_before_parent(self):
        fsm_category = self.env["fsm.category"]
        child = fsm_category.create({"name": "Child"})
        parent = fsm_category.create({"name": "Parent"})
        child.parent_id = parent
        self.env.invalidate_all()
        records = fsm_category.browse([child.id, parent.id])
        self.assertEqual(records.mapped("full_name"), ["Parent / Child", "Parent"])
