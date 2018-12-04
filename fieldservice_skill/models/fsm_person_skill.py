# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPersonSkill(models.Model):
    _name = 'fsm.person.skill'
    _description = 'Field Service Person Skill'

    person_id = fields.Many2one('fsm.person', string="Field Service Person")
    skill_id = fields.Many2one('hr.skill', string="Skill", required=True)
    level = fields.Selection([('0', 'Junior'),
                              ('1', 'Intermediate'),
                              ('2', 'Senior'),
                              ('3', 'Expert')], string='Level')

    _sql_constraints = [
        ('person_skill_uniq', 'unique(person_id, skill_id)',
         "This person already has that skill!"),
    ]
