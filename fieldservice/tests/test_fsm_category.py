# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import test_fsm_order


class TestFsmCategory(test_fsm_order.TestFSMOrder):
    def setUp(self):
        super().setUp()
        self.fsm_category_a = self.env["fsm.category"].create({"name": "Category A"})
        self.fsm_category_b = self.env["fsm.category"].create(
            {"name": "Category B", "parent_id": self.fsm_category_a.id}
        )

    def test_fsm_order_category(self):
        self.assertEqual(self.fsm_category_a.full_name, self.fsm_category_a.name)
        self.assertEqual(
            self.fsm_category_b.full_name,
            "%s/%s" % (self.fsm_category_a.name, self.fsm_category_b.name),
        )
