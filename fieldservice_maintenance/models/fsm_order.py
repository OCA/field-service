# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'
    _description = 'Field Service Order Maintenance'

    type = fields.Selection(selection_add=[('maintenance', 'Maintenance')])
    request_id = fields.Many2one(
        'maintenance.request', 'Maintenance Request')
