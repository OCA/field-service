# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrderCost(models.Model):
    _name = "fsm.order.cost"
    _inherit = "analytic.mixin"
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
        required=True,
        default=1,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        for cost in self:
            if not cost.product_id:
                continue
            cost.price_unit = cost.product_id.standard_price

    def _default_analytic_distribution(self):
        total_distribution = {}
        for order in self.fsm_order_id:
            if not order:
                return {}
            order_count = len(self.fsm_order_id)
            percentage_per_order = 100 / order_count

            analytic_account_ids = []

            order_id = self.env["fsm.order"].browse(order.id)

            analytic_account_id = order_id.location_id.analytic_account_id.id
            if analytic_account_id:
                analytic_account_ids.append(str(analytic_account_id))

            analytic_account_id = order_id.analytic_account_id.id
            if analytic_account_id:
                analytic_account_ids.append(str(analytic_account_id))

            if analytic_account_ids:
                distribution_key = ",".join(analytic_account_ids)
                total_distribution[distribution_key] = percentage_per_order

        self.analytic_distribution = total_distribution

        return total_distribution
