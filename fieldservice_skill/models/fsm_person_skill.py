# Copyright (C) 2018, Open Source Integrators
# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMPersonSkill(models.Model):
    _name = "fsm.person.skill"
    _rec_name = "skill_id"
    _description = "Field Service Worker Skill"

    person_id = fields.Many2one(
        "fsm.person", string="Field Service Worker", required=True
    )
    skill_id = fields.Many2one("hr.skill", string="Skill", required=True)
    skill_level_id = fields.Many2one("hr.skill.level", required=True)
    skill_type_id = fields.Many2one("hr.skill.type", required=True)
    level_progress = fields.Integer(related="skill_level_id.level_progress", store=True)

    _sql_constraints = [
        (
            "person_skill_uniq",
            "unique(person_id, skill_id)",
            "This person already has that skill!",
        ),
    ]

    @api.constrains("skill_id", "skill_type_id")
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _(
                        "The skill '%(skill)s' \
                        and skill type '%(skilltype)s' doesn't match",
                        skill=record.skill_id.name,
                        skilltype=record.skill_type_id.name,
                    )
                )

    @api.constrains("skill_type_id", "skill_level_id")
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(
                    _(
                        "The skill level '%(skilllevel)s' \
                        is not valid for skill type: '%(skilltype)s' ",
                        skilllevel=record.skill_level_id.name,
                        skilltype=record.skill_type_id.name,
                    )
                )
