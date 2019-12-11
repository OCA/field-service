# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    @api.multi
    def open_fieldservice_payments(self):
        return {'name': _('Payments'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('fsm_order_id', '=', self.id)],
                }
