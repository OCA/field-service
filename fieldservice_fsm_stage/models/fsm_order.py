# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrder(models.Model):
    _inherit = 'fsm.order'

    closing_date = fields.Datetime(
        string='Closing Date',
        help='The date when the order was closed.',
        compute='_compute_order_closed_date',
        store=True,
    )

    @api.depends('stage_id', 'stage_id.is_closed')
    def _compute_order_closed_date(self):
        for record in self:
            record.closing_date = (
                fields.Datetime.now() if record.stage_id.is_closed else False
            )
