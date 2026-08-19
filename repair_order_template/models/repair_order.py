# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    repair_order_template_id = fields.Many2one(
        string="Order Template",
        help="Use templates to save time when creating repair orders.",
        comodel_name="repair.order.template",
        check_company=True,
    )

    @api.constrains("repair_order_template_id")
    def _check_repair_order_template_id(self):
        if self.repair_order_template_id and self.state != "draft":
            raise ValidationError(
                self.env._("Order Template can only be set on draft orders")
            )

    @api.onchange("repair_order_template_id")
    def _onchange_repair_order_template_id(self):
        if not self.repair_order_template_id:
            return
        # Simple fields get copied over if they're set on the template
        for fname in ("product_id", "under_warranty", "tag_ids", "internal_notes"):
            if self.repair_order_template_id[fname]:
                self[fname] = self.repair_order_template_id[fname]
        # Lines get replaced by new ones, generated from the template lines
        if self.repair_order_template_id.line_ids:
            self.move_ids = [fields.Command.clear()] + [
                fields.Command.create(
                    dict(line._prepare_move_values(), company_id=self.company_id.id)
                )
                for line in self.repair_order_template_id.line_ids
            ]
