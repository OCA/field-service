# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import api, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    @api.multi
    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        for fsm_rec in self:
            fsm_route_obj = self.env['fsm.route']
            order_stage_id = self.env.ref('fieldservice.fsm_stage_scheduled',
                                          raise_if_not_found=False)
            if (vals.get('stage_id') and
                fsm_rec.stage_id.sequence >= order_stage_id.sequence) or \
                    (fsm_rec.stage_id.sequence >= order_stage_id.sequence and
                     (vals.get('scheduled_date_start') or
                      vals.get('person_id'))):
                fsm_route = fsm_route_obj.search([
                    ('person_id', '=', fsm_rec.person_id.id),
                    ('scheduled_date', '=', fsm_rec.scheduled_date_start)],
                    limit=1)
                if not fsm_route:
                    fsm_route = fsm_route_obj.create(
                        {'person_id': fsm_rec.person_id.id,
                         'scheduled_date': fsm_rec.scheduled_date_start,
                         'date': datetime.now()})
                fsm_rec.route_id = fsm_route.id
        return res
