# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMPreventiveType(models.Model):
    _name = "fsm.preventive.type"
    _description = "Field Service Preventive Visit Type"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    order_type_id = fields.Many2one(
        "fsm.order.type",
        string="Order Type",
        help="Type of the orders generated for visits of this type only.",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code of the visit type must be unique.")
    ]
