# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _description = 'Field Service Person'

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 delegate=True, auto_join=True)

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
