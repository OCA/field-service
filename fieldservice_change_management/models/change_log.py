# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangeLog(models.Model):
    _name = 'change.log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'implemented_on desc'
    _description = 'Change Log'

    active = fields.Boolean(default=True)
    name = fields.Char(string="Title", required=True)
    location_id = fields.Many2one('fsm.location', string="FSM Location")
    implemented_on = fields.Datetime(string="Implemented On", required=True,
                                     default=fields.Datetime.now)
    description = fields.Text(string="Description", required=True)
    user_id = fields.Many2one('res.users', string="Changed By",
                              default=lambda self: self.env.user,
                              track_visibility="onchange",
                              required="1")
    tag_ids = fields.Many2many('change.log.tag', string="Tags")
    type_id = fields.Many2one('change.log.type', string="Type", required=True)
    impact_id = fields.Many2one('change.log.impact', string="Impact",
                                required=True)
    change_log_sequence = fields.Integer(string="Sequence")
    color = fields.Integer()
    stage_id = fields.Many2one(
        'change.log.stage',
        string="Stage",
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id(),
        help="Select the current stage of the Bandwidth Change.")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('change.log') or '1000'
        vals['change_log_sequence'] = seq
        return super(ChangeLog, self).create(vals)

    @api.model
    def _default_stage_id(self):
        return self.env.ref(
            'fieldservice_change_management.change_log_stage_pending')
