# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    @api.model
    def get_default_customer(self):
        if self.fsm_parent_id:
            return self.fsm_parent_id.customer_id.id
        return self.owner_id.id

    customer_id = fields.Many2one(
        'res.partner', string='Customer', ondelete='restrict', auto_join=True,
        track_visibility='onchange', default=get_default_customer)

    @api.onchange('fsm_parent_id')
    def _onchange_customer(self):
        self.customer_id = self.fsm_parent_id.customer_id or False
