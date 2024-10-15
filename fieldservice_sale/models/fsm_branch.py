# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMBranch(models.Model):
    _inherit = 'fsm.branch'

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Default Pricelist',
        help="Default pricelist for new customers of this branch.")
