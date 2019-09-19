# Copyright (C) 2010 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Meeting(models.Model):

    _inherit = 'calendar.event'

    fsm_order_id = fields.One2many(
        string='Order id',
        comodel_name='fsm.order',
        inverse_name='calendar_event_id',
    )

    @api.multi
    def _update_fsm_order_date(self):
        self.ensure_one()
        if self._context.get('recurse_order_calendar'):
            # avoir recursion
            return
        to_apply = {}
        to_apply['scheduled_date_start'] = self.start
        to_apply['scheduled_duration'] = self.duration
        self.fsm_order_id.with_context(
            recurse_order_calendar=True
        ).write(to_apply)

    @api.multi
    def write(self, values):
        res = super().write(values)
        if self.fsm_order_id:
            self._update_fsm_order_date()
        return res
