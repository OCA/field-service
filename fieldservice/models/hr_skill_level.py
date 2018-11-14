# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HRSkillLevel(models.Model):
    _name = 'hr.skill.level'
    _description = 'Field Service Skill Level'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Skill Level already exists!"),
    ]
