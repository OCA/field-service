# Copyright (C) 2010 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Meeting',
        readonly=True,
        # ondelete='cascade',
        # TODO : gerer la supression proprement
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._create_calendar_event()
        return res

    @api.multi
    def _create_calendar_event(self):
        """ This method will create entry in calendar """
        # TODO: a quoi ça sert les activity ?
        # activity_id = self.env.ref('fsm_order_activity').id
        for order in self:
            order.calendar_event_id = self.env['calendar.event'].with_context(
                no_mail_to_attendees=True
            ).create(order._prepare_calendar_event())

    def _prepare_calendar_event(self):
        model_id = self.env.ref('fieldservice.model_fsm_order').id
        vals = {
            'name': self.name,
            'description': self.description,
            'start': self.scheduled_date_start,
            'stop': self.scheduled_date_end,
            'allday': False,
            'res_model_id': model_id,  # link back with "Document" button
            'res_id': self.id,  # link back with "Document" button
            'location': self._serialize_location(),
            'user_id': self.team_id.calendar_user_id.id,
        }
        if self.team_id.calendar_user_id:
            # if partner_ids = [], then no attendees to the event
            # if no partner_ids, then attendees is current user
            # here we set the calendar_user_id of the team as the attendee
            # instead of current user
            # because we want to use the calendar of calendar_user_id
            vals['partner_ids'] = [
                (4, self.team_id.calendar_user_id.partner_id.id, False)]
        return vals

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'scheduled_date_start' in vals or 'scheduled_date_end' in vals:
            self.update_calendar_date(vals)

        if 'location_id' in vals:
            self.update_calendar_location()
        if 'person_id' in vals:
            self.update_calendar_person()
        return res

    @api.multi
    def update_calendar_date(self, vals):
        if self._context.get('recurse_order_calendar'):
            # avoid recursion
            return
        to_apply = {}
        to_apply['start'] = self.scheduled_date_start
        to_apply['stop'] = self.scheduled_date_end
        # always write start and stop in order to calc duration
        self.mapped('calendar_event_id').with_context(
            recurse_order_calendar=True
        ).write(to_apply)

    @api.multi
    def update_calendar_location(self):
        for rec in self:
            rec.calendar_event_id.location = rec._serialize_location()

    def _serialize_location(self):
        partner_id = self.location_id.partner_id
        return '%s %s' % (partner_id.name, partner_id._display_address())

    @api.multi
    def update_calendar_person(self):
        for rec in self:
            if rec.person_id:
                rec.calendar_event_id.partner_ids = [
                    (4, rec.person_id.partner_id.id, False)
                ]
