# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class FSMRoute(models.Model):
    _inherit = 'fsm.route'
    vehicle_id = fields.Many2one('fsm.vehicle',
                                 string='Assigned Vehicle')

    _sql_constraints = [
        ('fsm_route_vehicle_date_uniq',
         'unique (vehicle_id, date)',
         _("The vehicle is already assigned to another route on that day!")),
    ]
