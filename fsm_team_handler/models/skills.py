# -*- coding: utf-8 -*-

from odoo import fields, models


class SkillsHandler(models.Model):
    _name = 'fsm.skills'
    _rec_name = 'name'
    _description = 'Manage skills'

    name = fields.Char(
        string="Skill Name",
        required=True
    )
