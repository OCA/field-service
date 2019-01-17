# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrSkill(models.Model):
    _inherit = 'hr.skill'

    color = fields.Integer('Color Index', default=0)