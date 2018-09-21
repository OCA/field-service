# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _inherits = {
        'res.partner': 'partner_id'
    }
    _description = 'Field Service Person'

    @api.model
    def create(self, vals):
        vals.update({
            'customer': False,
            'fsm_person': True,
        })
        return super(FSMPerson, self).create(vals)
