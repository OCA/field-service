# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMLocationSize(models.Model):
    _name = "fsm.location.size"
    _description = "Size for FSM Location"

    size_id = fields.Many2one("fsm.size", required=True, index=True)
    type_id = fields.Many2one("fsm.order.type", index=True, related="size_id.type_id")
    quantity = fields.Float(required=True)
    uom_id = fields.Many2one("uom.uom", index=True, related="size_id.uom_id")
    location_id = fields.Many2one(
        "fsm.location", string="Location", required=True, index=True
    )

    _sql_constraints = [
        (
            "one_size_per_location",
            "unique(location_id, size_id)",
            "Only one size of same type allowed per location",
        )
    ]
