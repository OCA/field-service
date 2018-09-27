# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FSMWizard(models.TransientModel):
    """
        A wizard to convert a res.partner record to a fsm.person or
         fsm.location
    """
    _name = 'fsm.wizard'
    _description = 'FSM Record Conversion'

    fsm_record_type = fields.Selection([('person', 'Person'),
                                        ('location', 'Location')],
                                       'Record Type')

    @api.multi
    def action_convert(self):
        self.ensure_one()
        partner_id = self._context.get('active_id')
        partner = self.env['res.partner'].search([('id', '=', partner_id)])
        if self.fsm_record_type == 'person':
            self.action_convert_person(partner)
        if self.fsm_record_type == 'location':
            self.action_convert_location(partner)
        return {'type': 'ir.actions.act_window_close'}

    def action_convert_location(self, partner):
        res = self.env['fsm.location'].search_count(
            [('partner_id', '=', partner.id)])
        if res == 0:
            self.env['fsm.location'].create({'partner_id': partner.id})
            partner.write({'fsm_location': True})
        else:
            raise UserError(_('A Field Service Location related to that'
                              ' partner already exists.'))

    def action_convert_person(self, partner):
        res = self.env['fsm.person'].search_count(
            [('partner_id', '=', partner.id)])
        if res == 0:
            self.env['fsm.person'].create({'partner_id': partner.id})
            partner.write({'fsm_person': True})
        else:
            raise UserError(_('A Field Service Person related to that'
                              ' partner already exists.'))
