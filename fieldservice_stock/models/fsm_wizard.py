# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


class FSMWizard(models.TransientModel):
    _inherit = 'fsm.wizard'

    def action_convert_location(self, partner):
        res = self.env['fsm.location'].search_count(
            [('partner_id', '=', partner.id)])
        if res == 0:
            vals = {'partner_id': partner.id,
                    'owner_id': partner.id,
                    'customer_id': partner.id,
                    'inventory_location_id':
                    partner.property_stock_customer.id}
            self.env['fsm.location'].create(vals)
            partner.write({'fsm_location': True})
        else:
            raise UserError(_('A Field Service Location related to that'
                              ' partner already exists.'))
        return res
