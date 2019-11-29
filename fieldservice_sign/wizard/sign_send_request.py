# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models, _


class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    fsm_order_id = fields.Many2one('fsm.order', 'FSM Order')

    def send_request(self):
        res = self.create_request()
        request = self.env['sign.request'].browse(res['id'])
        request.fsm_order_id = self.fsm_order_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Signature(s)'),
            'view_mode': 'form',
            'res_model': 'sign.request',
            'res_id': res['id']
        }
