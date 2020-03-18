# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    total_cost = fields.Float(compute='_compute_total_cost',
                              string='Total Cost')
    bill_to = fields.Selection([('location', 'Bill Location'),
                                ('contact', 'Bill Contact')],
                               string="Bill to",
                               required=True,
                               default="location")

    def _compute_total_cost(self):
        """ To be overridden as needed from other modules """
        for order in self:
            order.total_cost = 0.0
