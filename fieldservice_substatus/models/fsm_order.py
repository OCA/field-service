# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    sub_stage_id = fields.Many2one(
        'fsm.stage.status',
        string='Sub-Status',
        required=True,
        track_visibility='onchange',
        default=lambda self: self._default_stage_id().sub_stage_id)

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            sub_stage_id = self.env['fsm.stage'].browse(
                vals.get('stage_id')).sub_stage_id
            if sub_stage_id:
                vals.update({'sub_stage_id': sub_stage_id.id})
        return super(FSMOrder, self).write(vals)

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'sub_stage_id' in init_values:
            return 'fieldservice_substatus.fso_substatus_changed'
        return super()._track_subtype(init_values)
