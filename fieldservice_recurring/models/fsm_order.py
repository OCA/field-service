# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import models, fields, api


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    fsm_recurring_id = fields.Many2one(
        'fsm.recurring', 'Recurring Order', readonly=True)

    def _compute_request_late(self, vals):
        if not vals.get("fsm_recurring_id", False):
            return super(FSMOrder, self)._compute_request_late(vals)
        elif vals.get("scheduled_date_start", False):
            days_late = (
                self.env["fsm.recurring"]
                .browse(vals["fsm_recurring_id"])
                .fsm_frequency_set_id.buffer_late
            )
            vals["request_late"] = vals["scheduled_date_start"] + timedelta(
                days=days_late
            )
        return vals

    @api.multi
    def action_view_fsm_recurring(self):
        action = self.env.ref(
            'fieldservice_recurring.action_fsm_recurring').read()[0]
        action['views'] = [
            (self.env.ref(
                'fieldservice_recurring.fsm_recurring_form_view').id,
                'form')]
        action['res_id'] = self.fsm_recurring_id.id
        return action
