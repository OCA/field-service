# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    def _prepare_inv_line_for_stock_request(self, invoice=False):
        vals = super()._prepare_inv_line_for_stock_request(invoice)
        vals.update({
            'analytic_account_id': self.location_id.analytic_account_id.id,
        })
        return vals
