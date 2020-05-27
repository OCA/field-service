# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    change_log_count = fields.Integer(
        compute='_compute_change_log_count',
        string='# Change Logs'
    )
    change_log_ids = fields.One2many('change.log', 'location_id',
                                     string="Change Logs")

    @api.multi
    def _compute_change_log_count(self):
        for location in self:
            res = self.env['change.log'].search_count(
                [('location_id', '=', location.id)])
            location.change_log_count = res or 0

    @api.multi
    def action_open_change_logs(self):
        for location in self:
            change_log_ids = self.env['change.log'].search(
                [('location_id', '=', location.id)])
            action = self.env.ref(
                'fieldservice_change_management.change_log_action').read()[0]
            action['context'] = {}
            if len(change_log_ids) > 1:
                action['domain'] = [('id', 'in', change_log_ids.ids)]
            elif len(change_log_ids) == 1:
                action['views'] = [(self.env.ref(
                    'fieldservice_change_management.change_log_view_form').id,
                    'form')]
                action['res_id'] = change_log_ids.ids[0]
            return action
