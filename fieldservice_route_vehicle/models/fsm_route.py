# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmRoute(models.Model):
    _inherit = 'fsm.route'

    fsm_vehicle_id = fields.Many2one('fsm.vehicle',
                                     string='Vehicle')
