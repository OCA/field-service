# Copyright 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    @api.multi
    def action_create_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when creating an FSM Order from a ticket.
        """
        res = super().action_create_order()
        # override the context to get rid of the default filtering
        res['context'].update({
            'default_agreement_id': self.agreement_id.id,
            'default_serviceprofile_id': self.serviceprofile_id.id,
        })
        return res
