# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.tests import Form

from . import test_fsm_order


class TestTemplateOnchange(test_fsm_order.TestFSMOrder):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fsm_category_a = cls.env["fsm.category"].create({"name": "Category A"})
        cls.fsm_category_b = cls.env["fsm.category"].create({"name": "Category B"})
        cls.fsm_type_a = cls.env["fsm.order.type"].create({"name": "FSM Order Type A"})
        cls.fsm_team_a = cls.env["fsm.team"].create({"name": "FSM Team A"})

    def test_fsm_order_onchange_template(self):
        """Test the onchange function for FSM Template
        - Category IDs, Scheduled Duration,and Type should update
        - The instructions should be copied
        """
        categories = [self.fsm_category_a.id, self.fsm_category_b.id]
        self.fsm_template_1 = self.env["fsm.template"].create(
            {
                "name": "Test FSM Template #1",
                "instructions": "These are the instructions for Template #1",
                "category_ids": [(6, 0, categories)],
                "duration": 2.25,
                "type_id": self.fsm_type_a.id,
            }
        )
        self.fsm_template_2 = self.env["fsm.template"].create(
            {
                "name": "Test FSM Template #2",
                "instructions": "These are the instructions for Template #2",
                "category_ids": [(6, 0, categories)],
                "duration": 2.25,
                "team_id": self.fsm_team_a.id,
            }
        )
        self.env.user.write(
            {
                "groups_id": [
                    Command.link(self.env.ref("fieldservice.group_fsm_template").id),
                    Command.link(self.env.ref("fieldservice.group_fsm_category").id),
                ]
            }
        )
        default_team = self.Order._default_team_id()
        with Form(self.Order, view="fieldservice.fsm_order_form") as f:
            f.location_id = self.test_location
            f.scheduled_date_start = fields.Datetime.today()
            f.template_id = self.fsm_template_1
            self.assertEqual(f.category_ids.ids, self.fsm_template_1.category_ids.ids)
            self.assertEqual(f.scheduled_duration, self.fsm_template_1.duration)
            self.assertEqual(f.type.id, self.fsm_template_1.type_id.id)
            self.assertEqual(f.todo, self.fsm_template_1.instructions)
            # Team should be the default one since template 1 has no team
            self.assertEqual(f.team_id.id, default_team.id)

            # Change the template
            f.template_id = self.fsm_template_2
            self.assertEqual(f.category_ids.ids, self.fsm_template_2.category_ids.ids)
            self.assertEqual(f.scheduled_duration, self.fsm_template_2.duration)
            # Type should remain the same since template 2 has no type
            self.assertEqual(f.type.id, self.fsm_type_a.id)
            self.assertEqual(f.todo, self.fsm_template_2.instructions)
            # Team should be changed since template 2 has a team
            self.assertEqual(f.team_id.id, self.fsm_template_2.team_id.id)
