# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HRSkill(models.Model):
    _inherit = "hr.skill"

    color = fields.Integer(
        string="Color Index",
        default=10,
    )
