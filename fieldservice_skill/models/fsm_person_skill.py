# Copyright (C) 2018, Open Source Integrators
# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FSMPersonSkill(models.Model):
    _name = "fsm.person.skill"
    _rec_name = "skill_id"
    _description = "Field Service Worker Skill"

    person_id = fields.Many2one(
        "fsm.person", string="Field Service Worker", required=True
    )
    skill_id = fields.Many2one(
        "hr.skill",
        compute="_compute_skill_id",
        store=True,
        domain="[('skill_type_id', '=', skill_type_id)]",
        readonly=False,
        required=True,
        ondelete="cascade",
    )
    skill_level_id = fields.Many2one(
        "hr.skill.level",
        compute="_compute_skill_level_id",
        domain="[('skill_type_id', '=', skill_type_id)]",
        store=True,
        readonly=False,
        required=True,
        ondelete="cascade",
    )
    skill_type_id = fields.Many2one(
        "hr.skill.type",
        default=lambda self: self.env["hr.skill.type"].search([], limit=1),
        required=True,
        ondelete="cascade",
    )

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
                    self.env._(
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
                    self.env._(
                        "The skill level '%(skilllevel)s' \
                        is not valid for skill type: '%(skilltype)s' ",
                        skilllevel=record.skill_level_id.name,
                        skilltype=record.skill_type_id.name,
                    )
                )

    @api.depends("skill_type_id")
    def _compute_skill_id(self):
        for record in self:
            if record.skill_type_id:
                record.skill_id = (
                    record.skill_type_id.skill_ids[0]
                    if record.skill_type_id.skill_ids
                    else False
                )
            else:
                record.skill_id = False

    @api.depends("skill_id")
    def _compute_skill_level_id(self):
        for record in self:
            if not record.skill_id:
                record.skill_level_id = False
            else:
                skill_levels = record.skill_type_id.skill_level_ids
                record.skill_level_id = (
                    skill_levels.filtered("default_level") or skill_levels[0]
                    if skill_levels
                    else False
                )
