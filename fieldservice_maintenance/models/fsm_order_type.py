# Copyright 2020 - TODAY Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmOrderType(models.Model):

    _inherit = 'fsm.order.type'

    internal_type = fields.Selection(
        selection_add=[('maintenance',
                        'Maintenance')],
    )
