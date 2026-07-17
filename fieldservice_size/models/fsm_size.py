# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class FSMSize(models.Model):
    _name = "fsm.size"
    _description = "Field Service Size"

    name = fields.Char(required=True)
    type_id = fields.Many2one("fsm.order.type", string="Order Type")
    parent_id = fields.Many2one("fsm.size", string="Parent Size", index=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    is_order_size = fields.Boolean(
        string="Is the Order Size?", help="The default size for orders of this type"
    )

    _name_uniq = models.Constraint(
        "unique (name)",
        "Size name already exists!",
    )

    @api.constrains("is_order_size", "type_id")
    def _one_size_per_type(self):
        for rec in self:
            size_count = self.search_count(
                Domain([("type_id", "=", rec.type_id.id), ("is_order_size", "=", True)])
            )
            if size_count >= 2:
                raise ValidationError(
                    self.env._("Only one default order size per type is allowed.")
                )
