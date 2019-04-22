# Copyright (C) 2019 - TODAY, Open Source Integrators, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMStageStatus(models.Model):
    _name = 'fsm.stage.status'
    _description = 'Order Sub-Status'

    name = fields.Char(string='Name', required=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        context = self._context or {}
        if context.get('fsm_order_stage_id'):
            stage_id = self.env['fsm.stage'].browse(context.get(
                'fsm_order_stage_id'))
            sub_stage_ids = stage_id.sub_stage_id + stage_id.sub_stage_ids
            if sub_stage_ids:
                args = [('id', 'in', sub_stage_ids.ids)]
        return super(FSMStageStatus, self)._search(
            args, offset, limit, order, count=count,
            access_rights_uid=access_rights_uid)
