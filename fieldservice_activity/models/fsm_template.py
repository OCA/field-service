# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTemplate(models.Model):
    _inherit = "fsm.template"

    temp_activity_ids = fields.One2many("fsm.activity", "fsm_template_id", "Activities")
