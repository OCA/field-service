# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    create_fsm_equipment = fields.Boolean(
        string="Creates a FSM Equipment",
        help="Creates a Field Service Equipment when a stock move is done. "
        "It requires the 'Create FSM Equipment' option to be enabled on the "
        "picking type, too.",
    )
