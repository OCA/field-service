# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMSkill(models.Model):
    _inherit = 'hr.skill'
    _name = 'fsm.skill'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Skill name already exists!"),
    ]

    skill_level = fields.Many2one('hr.skill.level', string='Skill Level')
    