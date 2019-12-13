# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    dayroute_id = fields.Many2one('fsm.route.dayroute',
                                  string='Day Route',
                                  index=True)
    fsm_route_id = fields.Many2one(related="location_id.fsm_route_id",
                                   string='Route')

    def _manage_fsm_route(self, vals):
        fsm_route_obj = self.env['fsm.route.dayroute']
        for rec in self:
            old_route_id = False
            person_id = vals.get('person_id') or rec.person_id.id
            scheduled_date_start = vals.get('scheduled_date_start') or \
                rec.scheduled_date_start
            fsm_route = fsm_route_obj.search([
                ('person_id', '=', person_id),
                ('date', '=', scheduled_date_start)],
                limit=1)
            old_route_id = rec.dayroute_id
            if fsm_route:
                rec.dayroute_id = fsm_route.id
                if old_route_id and not old_route_id.order_ids:
                    old_route_id.unlink()
            elif not fsm_route and person_id or scheduled_date_start:
                fsm_route_obj.create({
                    'person_id': person_id,
                    'date': scheduled_date_start,
                    'route_id': rec.fsm_route_id.id,
                    'order_ids': [(4, rec.id)]
                })
                if old_route_id and not old_route_id.order_ids:
                    old_route_id.unlink()

    @api.model
    def create(self, vals):
        res = super(FSMOrder, self).create(vals)
        if res.person_id and res.scheduled_date_start:
            res._manage_fsm_route(vals)
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('person_id') or vals.get('scheduled_date_start'):
                rec._manage_fsm_route(vals)
        return super(FSMOrder, self).write(vals)
