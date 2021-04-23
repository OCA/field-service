# Copyright (C) 2018, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMCategory(models.Model):
    _inherit = "fsm.category"

    skill_ids = fields.Many2many("hr.skill", string="Required Skills")
