# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    @api.model
    def _get_default_person(self):
        return self.fsm_route_id.fsm_person_id.id or False

    dayroute_id = fields.Many2one('fsm.route.dayroute',
                                  string='Day Route',
                                  index=True)
    fsm_route_id = fields.Many2one(related="location_id.fsm_route_id",
                                   string='Route')

    person_id = fields.Many2one(
        'fsm.person', string='Assigned To', index=True,
        default=_get_default_person)

    def prepare_dayroute_values(self, person_id, date_start):
        return {
            'person_id': person_id,
            'date': date_start,
            'route_id': self.fsm_route_id.id,
            'team_id': self.team_id.id,
            'order_ids': [(4, self.id)]
        }

    def _manage_fsm_route(self, vals):
        fsm_route_obj = self.env['fsm.route.dayroute']
        for rec in self:
            old_route_id = False
            person_id = vals.get('person_id') or rec.person_id.id or \
                        rec.fsm_route_id.fsm_person_id.id
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
                fsm_route_obj.create(rec.prepare_dayroute_values(
                    person_id, scheduled_date_start
                ))
                if old_route_id and not old_route_id.order_ids:
                    old_route_id.unlink()

    @api.model
    def create(self, vals):
        if not vals.get('person_id'):
            location = self.env['fsm.location'].browse(vals.get('location_id'))
            vals.update({
                'person_id': location.fsm_route_id.fsm_person_id.id,
            })
        res = super(FSMOrder, self).create(vals)
        if res.person_id and res.scheduled_date_start:
            res._manage_fsm_route(vals)
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('route_id', False):
                route = self.env['fsm.route'].browse(vals.get('route_id'))
                vals.update({
                    'person_id': route.person_id.id,
                    'scheduled_date_start': route.date,
                })
            if vals.get('person_id', False) or \
                    vals.get('scheduled_date_start', False):
                rec._manage_fsm_route(vals)
        return super(FSMOrder, self).write(vals)
