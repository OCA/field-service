# models/sale_order.py

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _link_pickings_to_fsm(self):
        res = super()._link_pickings_to_fsm()
        for rec in self:
            fsm_orders = self._get_related_fsm_orders(rec.id)
            fsm_orders._sync_tags_from_products()

        return res

    def write(self, vals):
        res = super().write(vals)

        if "order_line" in vals and self._is_new_order_line(vals["order_line"]):
            products = self._get_products_from_order_lines(vals["order_line"])
            for order in self:
                fsm_orders = self._get_related_fsm_orders(order.id)
                for product in products:
                    fsm_orders._add_tags_for_product(product)

        return res

    def _get_related_fsm_orders(self, sale_id):
        """Retrieve FSM orders related to the given sale order ID."""
        return self.env["fsm.order"].search(
            [
                ("sale_id", "=", sale_id),
                ("sale_line_id", "=", False),
                ("is_closed", "=", False),
            ]
        )

    def _is_new_order_line(self, order_line_vals):
        """Check if the order line values indicate a new line is being added."""
        return order_line_vals[-1][0] == 0

    def _get_products_from_order_lines(self, order_line_vals):
        """Retrieve all products from the order line values."""
        product_ids = [
            line[2]["product_id"]
            for line in order_line_vals
            if line[0] == 0 and "product_id" in line[2]
        ]
        return self.env["product.product"].browse(product_ids)
