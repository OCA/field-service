# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    location_latitude = fields.Float(related='location_id.partner_latitude',
                                     string='Location Latitude')
    location_longitude = fields.Float(related='location_id.partner_longitude',
                                      string='Location Longitude')
    marker_color = fields.Char(related='stage_id.custom_color',
                               string='Marker Color')
