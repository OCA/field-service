# Copyright 2020, Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMSkill(TransactionCase):
    def setUp(self):
        super().setUp()

        self.skill = self.env["hr.skill"]
        self.skill_level = self.env["hr.skill.level"]
        self.skill_type = self.env["hr.skill.type"]
        self.fsm_person = self.env["fsm.person"]
        self.fsm_person_skill = self.env["fsm.person.skill"]
        self.fsm_order = self.env["fsm.order"]
        self.fsm_location = self.env["fsm.location"]
        self.fsm_template = self.env["fsm.template"]
        self.fsm_category = self.env["fsm.category"]

        self.skill_type_01 = self.skill_type.create({"name": "Field Service Skills"})

        self.skill_type_03 = self.skill_type.create({"name": "Field Service Skills 3"})

        # Create some great skills
        self.skill_01 = self.skill.create(
            {"name": "Nunchuck Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_02 = self.skill.create(
            {"name": "Bow Hunting Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_03 = self.skill.create(
            {"name": "Computer Hacking Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_04 = self.skill.create(
            {"name": "Sweet Bike Owning Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_05 = self.skill.create(
            {
                "name": "Hooking Up with Chicks Skills",
                "skill_type_id": self.skill_type_01.id,
            }
        )
        self.skill_06 = self.skill.create(
            {"name": "Moustache Growing Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_07 = self.skill.create(
            {"name": "Growing Skills", "skill_type_id": self.skill_type_01.id}
        )
        self.skill_08 = self.skill.create(
            {"name": "Computer Growing Skills", "skill_type_id": self.skill_type_01.id}
        )

        self.skill_level_100 = self.skill_level.create(
            {
                "name": "Great",
                "skill_type_id": self.skill_type_01.id,
                "level_progress": 100,
            }
        )
        self.skill_level_101 = self.skill_level.create(
            {
                "name": "Great",
                "skill_type_id": self.skill_type_01.id,
                "level_progress": 100,
            }
        )

        # Create some great workers with their own great skills
        # Our first worker, Napoleon, has nunchuck skills and bow hunting
        # skills, which he learned while in Alaska hunting wolverines with his
        # uncle.
        self.person_01 = self.fsm_person.create({"name": "Napoleon"})
        self.person_01_skill_01 = self.fsm_person_skill.create(
            {
                "person_id": self.person_01.id,
                "skill_id": self.skill_01.id,
                "skill_level_id": self.skill_level_100.id,
                "skill_type_id": self.skill_type_01.id,
            }
        )
        self.person_01_skill_02 = self.fsm_person_skill.create(
            {
                "person_id": self.person_01.id,
                "skill_id": self.skill_02.id,
                "skill_level_id": self.skill_level_100.id,
                "skill_type_id": self.skill_type_01.id,
            }
        )

        # Our second worker, Pedro, has a lot of really good skills which he
        # learned from his cousins that have all the sweet hookups
        self.person_02 = self.fsm_person.create({"name": "Pedro"})
        self.person_02_skill_04 = self.fsm_person_skill.create(
            {
                "person_id": self.person_02.id,
                "skill_id": self.skill_04.id,
                "skill_level_id": self.skill_level_100.id,
                "skill_type_id": self.skill_type_01.id,
            }
        )
        self.person_02_skill_05 = self.fsm_person_skill.create(
            {
                "person_id": self.person_02.id,
                "skill_id": self.skill_05.id,
                "skill_level_id": self.skill_level_100.id,
                "skill_type_id": self.skill_type_01.id,
            }
        )
        self.person_02_skill_06 = self.fsm_person_skill.create(
            {
                "person_id": self.person_02.id,
                "skill_id": self.skill_06.id,
                "skill_level_id": self.skill_level_100.id,
                "skill_type_id": self.skill_type_01.id,
            }
        )

        # Create a location for an order
        self.location_01 = self.fsm_location.create(
            {
                "name": "Summer's House",
                "owner_id": self.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )

        # Create a category that requires great skills
        self.category_01_skills = [self.skill_04.id, self.skill_05.id, self.skill_06.id]
        self.category_01 = self.fsm_category.create(
            {"name": "Sales", "skill_ids": [Command.set(self.category_01_skills)]}
        )
        self.category_02_skills = [self.skill_05.id, self.skill_06.id, self.skill_07.id]
        self.category_02 = self.fsm_category.create(
            {"name": "Sales1", "skill_ids": [Command.set(self.category_02_skills)]}
        )
        self.skill_type_02 = self.skill_type.create(
            {
                "name": "Field Service Skills 2",
                "skill_ids": [Command.set(self.category_02_skills)],
            }
        )
        # Create a template that requires great skills
        self.template_01_skills = [self.skill_01.id, self.skill_02.id]
        self.template_01 = self.fsm_template.create(
            {
                "name": "Template Name",
                "skill_ids": [Command.set(self.template_01_skills)],
            }
        )

        # Create an order that requires no skills
        self.order_no_skills = self.fsm_order.create(
            {"location_id": self.location_01.id}
        )

        # Create an order with a category
        self.order_category_skills = self.fsm_order.create(
            {
                "location_id": self.location_01.id,
                "category_ids": [Command.set([self.category_01.id])],
            }
        )

        # Create an order with a template
        self.order_template_skills = self.fsm_order.create(
            {"location_id": self.location_01.id, "template_id": self.template_01.id}
        )

    def test_fsm_skills(self):
        # Validate the order without skills can be done by all workers
        self.assertEqual(
            self.order_no_skills.skill_worker_ids.ids,
            self.fsm_person.search([]).ids,
            "FSM Order without skills should allow all workers",
        )

        # Trigger the category onchange and validate skill_ids get set
        self.order_category_skills._onchange_category_ids()
        self.assertEqual(
            self.order_category_skills.skill_ids.ids,
            self.category_01_skills,
            "The order should have skills based on the category",
        )

        # Trigger the template onchange and validate skill_ids get set
        self.order_template_skills._onchange_template_id()
        self.assertEqual(
            self.order_template_skills.skill_ids.ids,
            self.template_01_skills,
            "The order should have skills based on the template",
        )

        # Validate the skilled order can be done by Pedro who has the skills
        self.assertEqual(
            self.order_category_skills.skill_worker_ids,
            self.person_02,
            "FSM Order should only allow workers with all skills required",
        )

    def test_constrains_skill_01(self):
        with self.assertRaises(ValidationError):
            self.fsm_person_skill.create(
                {
                    "person_id": self.person_01.id,
                    "skill_id": self.skill_07.id,
                    "skill_level_id": self.skill_level_100.id,
                    "skill_type_id": self.skill_type_01.id,
                }
            )

    def test_constrains_skill_level_100(self):
        with self.assertRaises(ValidationError):
            self.fsm_person_skill.create(
                {
                    "person_id": self.person_01.id,
                    "skill_id": self.skill_08.id,
                    "skill_level_id": self.skill_level_101.id,
                    "skill_type_id": self.skill_type_03.id,
                }
            )
