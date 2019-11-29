# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    sign_request_ids = fields.One2many('sign.request', 'fsm_order_id',
                                       string='Requested Signatures')
