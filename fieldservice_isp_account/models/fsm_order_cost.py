# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrderCost(models.Model):

    _name = "fsm.order.cost"
    _description = "Fsm Order Cost"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        required=True,
    )
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
    )
    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        for cost in self:
            if not cost.product_id:
                continue
            cost.price_unit = cost.product_id.standard_price
