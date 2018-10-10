# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _name = 'fsm.location'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Field Service Location'

    direction = fields.Char(string='Directions')
    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 auto_join=True)
    owner_id = fields.Many2one('res.partner', string='Related Owner',
                                 required=True, ondelete='restrict',
                                 auto_join=True)
    customer_id = fields.Many2one('res.partner', string='Related Customer',
                                 required=True, ondelete='restrict',
                                 auto_join=True)
    location_type_ids = fields.Many2many('fsm.tag',
        'location_type_fsm_tag', 'fsm_location_id', 'loc_type_id',
        string='Location Type')
    location_material_ids = fields.Many2many('fsm.tag',
        'location_material_fsm_tag', 'fsm_location_id', 'loc_material_id',
        string='Location Material')
    tanent_categ_ids = fields.Many2many('fsm.tag',
        'tanent_categ_fsm_tag', 'fsm_location_id', 'tanent_categ_id',
        string='Tanent Category')
    location_destination_ids = fields.Many2many('fsm.tag',
        'location_destination_fsm_tag', 'fsm_location_id', 'loc_destination_id',
        string='Location Destination')
    building = fields.Char(string='Building', size=35)
    floor = fields.Char(string='Floor', size=35)
    unit = fields.Char(string='Unit', size=35)
    room = fields.Char(string='Room', size=35)
    fsm_longitude = fields.Float(string='FSM Longitude')
    fsm_latitude = fields.Float(string='FSM Latitude')
    description = fields.Char(string='Description')
    territory = fields.Char(string='Territory', size=35)
    branch = fields.Char(string='Branch', size=35)
    district = fields.Char(string='District', size=35)
    region = fields.Char(string='Region', size=35)
    fsm_address1 = fields.Char(string='FSM Address1', size=35)
    fsm_address2 = fields.Char(string='FSM Address2', size=35)
    fsm_city = fields.Char(string='FSM City', size=35)
    fsm_state = fields.Char(string='FSM State', size=35)
    fsm_country = fields.Char(string='FSM Country', size=35)
    fsm_postal = fields.Char(string='FSM Postal', size=35)
    timezone = fields.Char(string='Timezone', size=35)
    
    @api.model
    def create(self, vals):
        vals.update({'fsm_location': True})
        return super(FSMLocation, self).create(vals)