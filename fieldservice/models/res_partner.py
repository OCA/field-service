# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fsm_location = fields.Boolean('Is a FS Location')
    fsm_person = fields.Boolean('Is a FS Worker')
    service_location_id = fields.Many2one('fsm.location',
                                          string='Primary Service Location')
    owned_location_ids = fields.One2many('fsm.location',
                                         'owner_id',
                                         string='Owned Locations',
                                         domain=[('fsm_parent_id', '=', False)]
                                         )
