# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


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

    def prepare_dayroute_values(self, values):
        return {
            'person_id': values['person_id'],
            'date': values['date'],
            'route_id': values['route_id']}

    def _get_dayroute_values(self, vals):
        date = False
        if vals.get('scheduled_date_start'):
            if type(vals.get('scheduled_date_start')) == str:
                date = datetime.strptime(vals.get('scheduled_date_start'),
                                         DEFAULT_SERVER_DATETIME_FORMAT).date()
            elif isinstance(vals.get('scheduled_date_start'), datetime):
                date = vals.get('scheduled_date_start').date()
        return {
            'person_id':
                vals.get('person_id') or self.person_id.id or
                self.fsm_route_id.fsm_person_id.id,
            'date': date or self.scheduled_date_start.date(),
            'route_id': vals.get('fsm_route_id') or self.fsm_route_id.id,
        }

    def _get_dayroute_domain(self, values):
        domain = [('person_id', '=', values['person_id']),
                  ('date', '=', values['date']),
                  ('order_remaining', '>', 0)]
        return domain

    def _can_create_dayroute(self, values):
        return values['person_id'] and values['date']

    def _manage_fsm_route(self, vals):
        dayroute_obj = self.env['fsm.route.dayroute']
        values = self._get_dayroute_values(vals)
        domain = self._get_dayroute_domain(values)
        dayroute = dayroute_obj.search(domain, limit=1)
        if dayroute:
            vals.update({'dayroute_id': dayroute.id})
        else:
            if self._can_create_dayroute(values):
                dayroute = dayroute_obj.create(
                    self.prepare_dayroute_values(values))
                vals.update({
                    'dayroute_id': dayroute.id})
        # If this was the last order of the dayroute,
        # delete the dayroute
        if self.dayroute_id and not self.dayroute_id.order_ids:
            self.dayroute_id.unlink()
        return vals

    @api.model
    def create(self, vals):
        location = self.env['fsm.location'].browse(vals.get('location_id'))
        if not vals.get('fsm_route_id'):
            vals.update({
                'fsm_route_id': location.fsm_route_id.id})
        if not vals.get('person_id'):
            vals.update({
                'person_id': location.fsm_route_id.fsm_person_id.id})
        if vals.get('person_id') and vals.get('scheduled_date_start'):
            vals = self._manage_fsm_route(vals)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('route_id', False):
                route = self.env['fsm.route'].browse(vals.get('route_id'))
                vals.update({
                    'person_id': route.person_id.id,
                    'scheduled_date_start': route.date,
                })
            if (vals.get('person_id', False) or rec.person_id) and \
                    (vals.get('scheduled_date_start', False) or
                     rec.scheduled_date_start):
                vals = rec._manage_fsm_route(vals)
        return super().write(vals)
