# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import test_fsm_order


class TestFsmCategory(test_fsm_order.TestFSMOrder):
    def setUp(self):
        super(TestFsmCategory, self).setUp()
        self.fsm_category_a = self.env["fsm.category"].create({"name": "Category A"})
        self.fsm_category_b = self.env["fsm.category"].create(
            {"name": "Category B", "parent_id": self.fsm_category_a.id}
        )

    def test_fsm_order_category(self):
        self.fsm_category_a._compute_full_name()
        self.fsm_category_b._compute_full_name()
