# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Field Service Worker'

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 delegate=True, auto_join=True)
    category_ids = fields.Many2many('fsm.category', string='Categories')
    calendar_id = fields.Many2one('resource.calendar',
                                  string='Working Schedule')
    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               track_visibility='onchange',
                               index=True, copy=False,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id())
    hide = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        vals.update({'fsm_person': True})
        return super(FSMPerson, self).create(vals)

    @api.multi
    def get_person_information(self, vals):
        # get person ids
        person_ids = self.search([('id', '!=', 0), ('active', '=', True)])
        person_information_dict = []
        for person in person_ids:
            person_information_dict.append({
                'id': person.id,
                'name': person.name})
        return person_information_dict

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].search([('stage_type',
                                                   '=', 'worker')])
        return stage_ids

    def _default_stage_id(self):
        return self.env['fsm.stage'].search([('stage_type', '=', 'worker'),
                                             ('sequence', '=', '1')])

    def advance_stage(self):
        seq = self.stage_id.sequence
        next_stage = self.env['fsm.stage'].search(
            [('stage_type', '=', 'worker'), ('sequence', '=', seq + 1)])
        self.stage_id = next_stage
        self._onchange_stage_id()

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        # get last stage
        heighest_stage = self.env['fsm.stage'].search(
            [('stage_type', '=', 'worker')],
            order='sequence desc',
            limit=1)
        if self.stage_id.name == heighest_stage.name:
            self.hide = True
        else:
            self.hide = False
