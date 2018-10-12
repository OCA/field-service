# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FSMRoute(models.Model):
    _name = 'fsm.route'
    _description = 'Field Service Route'
    _order = 'date, name'

    name = fields.Char(string='Name', required=True,
                       default=lambda self: _('New'))
    fsm_order_ids = fields.One2many('fsm.order', 'fsm_route_id',
                                    string='Orders')
    fsm_person_id = fields.Many2one('fsm.person',
                                    string='Assigned To',
                                    required=True)
    fsm_vehicle_id = fields.Many2one('fsm.vehicle',
                                     string='Assigned Vehicle')
    date = fields.Date(string='Date', required=True)

    _sql_constraints = [
        ('fsm_route_person_date_uniq',
         'unique (fsm_person_id, date)',
         "You cannot create 2 routes for the same person on the same day!"),
        ('fsm_route_vehicle_date_uniq',
         'unique (fsm_vehicle_id, date)',
         "You cannot create 2 routes for the same vehicle on the same day!"),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.route')\
                or _('New')
        return super(FSMRoute, self).create(vals)
