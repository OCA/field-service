# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    marker_color = fields.Char(related='stage_id.custom_color',
                               string='Marker Color')
