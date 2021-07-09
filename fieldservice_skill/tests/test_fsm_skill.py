# Copyright 2020, Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests import SavepointCase


class TestFSMSkill(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFSMSkill, cls).setUpClass()

        cls.skill = cls.env["hr.skill"]
        cls.skill_level = cls.env["hr.skill.level"]
        cls.skill_type = cls.env["hr.skill.type"]
        cls.fsm_person = cls.env["fsm.person"]
        cls.fsm_person_skill = cls.env["fsm.person.skill"]
        cls.fsm_order = cls.env["fsm.order"]
        cls.fsm_location = cls.env["fsm.location"]
        cls.fsm_template = cls.env["fsm.template"]
        cls.fsm_category = cls.env["fsm.category"]

        cls.skill_type_01 = cls.skill_type.create({"name": "Field Service Skills"})

        # Create some great skills
        cls.skill_01 = cls.skill.create(
            {"name": "Nunchuck Skills", "skill_type_id": cls.skill_type_01.id}
        )
        cls.skill_02 = cls.skill.create(
            {"name": "Bow Hunting Skills", "skill_type_id": cls.skill_type_01.id}
        )
        cls.skill_03 = cls.skill.create(
            {"name": "Computer Hacking Skills", "skill_type_id": cls.skill_type_01.id}
        )
        cls.skill_04 = cls.skill.create(
            {"name": "Sweet Bike Owning Skills", "skill_type_id": cls.skill_type_01.id}
        )
        cls.skill_05 = cls.skill.create(
            {
                "name": "Hooking Up with Chicks Skills",
                "skill_type_id": cls.skill_type_01.id,
            }
        )
        cls.skill_06 = cls.skill.create(
            {"name": "Moustache Growing Skills", "skill_type_id": cls.skill_type_01.id}
        )

        cls.skill_level_100 = cls.skill_level.create(
            {
                "name": "Great",
                "skill_type_id": cls.skill_type_01.id,
                "level_progress": 100,
            }
        )

        # Create some great workers with their own great skills
        # Our first worker, Napoleon, has nunchuck skills and bow hunting
        # skills, which he learned while in Alaska hunting wolverines with his
        # uncle.
        cls.person_01 = cls.fsm_person.create({"name": "Napoleon"})
        cls.person_01_skill_01 = cls.fsm_person_skill.create(
            {
                "person_id": cls.person_01.id,
                "skill_id": cls.skill_01.id,
                "skill_level_id": cls.skill_level_100.id,
                "skill_type_id": cls.skill_type_01.id,
            }
        )
        cls.person_01_skill_02 = cls.fsm_person_skill.create(
            {
                "person_id": cls.person_01.id,
                "skill_id": cls.skill_02.id,
                "skill_level_id": cls.skill_level_100.id,
                "skill_type_id": cls.skill_type_01.id,
            }
        )

        # Our second worker, Pedro, has a lot of really good skills which he
        # learned from his cousins that have all the sweet hookups
        cls.person_02 = cls.fsm_person.create({"name": "Pedro"})
        cls.person_02_skill_04 = cls.fsm_person_skill.create(
            {
                "person_id": cls.person_02.id,
                "skill_id": cls.skill_04.id,
                "skill_level_id": cls.skill_level_100.id,
                "skill_type_id": cls.skill_type_01.id,
            }
        )
        cls.person_02_skill_05 = cls.fsm_person_skill.create(
            {
                "person_id": cls.person_02.id,
                "skill_id": cls.skill_05.id,
                "skill_level_id": cls.skill_level_100.id,
                "skill_type_id": cls.skill_type_01.id,
            }
        )
        cls.person_02_skill_06 = cls.fsm_person_skill.create(
            {
                "person_id": cls.person_02.id,
                "skill_id": cls.skill_06.id,
                "skill_level_id": cls.skill_level_100.id,
                "skill_type_id": cls.skill_type_01.id,
            }
        )

        # Create a location for an order
        cls.location_01 = cls.fsm_location.create(
            {
                "name": "Summer's House",
                "owner_id": cls.env["res.partner"]
                .create({"name": "Summer's Parents"})
                .id,
            }
        )

        # Create a category that requires great skills
        cls.category_01_skills = [cls.skill_04.id, cls.skill_05.id, cls.skill_06.id]
        cls.category_01 = cls.fsm_category.create(
            {"name": "Sales", "skill_ids": [(6, 0, cls.category_01_skills)]}
        )

        # Create a template that requires great skills
        cls.template_01_skills = [cls.skill_01.id, cls.skill_02.id]
        cls.template_01 = cls.fsm_template.create(
            {"name": "Template Name", "skill_ids": [(6, 0, cls.template_01_skills)]}
        )

        # Create an order that requires no skills
        cls.order_no_skills = cls.fsm_order.create({"location_id": cls.location_01.id})

        # Create an order with a category
        cls.order_category_skills = cls.fsm_order.create(
            {
                "location_id": cls.location_01.id,
                "category_ids": [(6, 0, [cls.category_01.id])],
            }
        )

        # Create an order with a template
        cls.order_template_skills = cls.fsm_order.create(
            {"location_id": cls.location_01.id, "template_id": cls.template_01.id}
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
