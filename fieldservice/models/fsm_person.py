# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Field Service Worker'

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 delegate=True, auto_join=True)
    category_ids = fields.Many2many('fsm.category', string='Categories')
    location_id = fields.Many2one('fsm.location',
                                  string='Preferred Location')
    territory_ids = fields.Many2many('fsm.territory', string='Territories')
    calendar_id = fields.Many2one('resource.calendar',
                                  string='Working Schedule')
    location_ids = fields.Many2many('fsm.location',
                                    string='Linked Locations',
                                    compute='_compute_location_ids')

    @api.model
    def create(self, vals):
        vals.update({'fsm_person': True})
        return super(FSMPerson, self).create(vals)

    @api.multi
    def get_person_information(self, vals):
        # get person ids
        person_ids = self.search([('id', '!=', 0), ('active', '=', True)])
        person_information_dict = []
        for person in person_ids:
            person_information_dict.append({
                'id': person.id,
                'name': person.name})
        return person_information_dict

    @api.multi
    def _compute_location_ids(self):
        for line in self:
            ids = []
            locations = self.env['fsm.location'].search([])
            for loc in locations:
                if line in loc.person_ids:
                    ids.append(loc.name)
            locations = self.env['fsm.location'].search([('name', 'in', ids)])
            line.location_ids = locations
