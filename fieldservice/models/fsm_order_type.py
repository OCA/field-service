# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrderType(models.Model):
    _name = "fsm.order.type"
    _description = "Field Service Order Type"

    name = fields.Char(string="Name")

    internal_type = fields.Selection(
        string="Internal Type",
        selection=[("fsm", "FSM")],
        default="fsm",
    )
