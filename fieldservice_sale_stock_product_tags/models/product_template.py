# models/product_template.py

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)

        if "tag_ids" in vals:
            self._update_fsm_orders_tag_ids()

        return res

    def _update_fsm_orders_tag_ids(self):
        products = self.mapped("product_variant_ids")

        fsm_orders = self.env["fsm.order"].search(
            [
                ("move_ids.product_id", "in", products.ids),
                ("stage_id.is_closed", "=", False),
            ]
        )

        fsm_orders._sync_tags_from_products()
