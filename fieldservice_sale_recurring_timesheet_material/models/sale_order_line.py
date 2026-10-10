# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_invoiceable_fsm_order_domain(self):
        """
        The default domain looks for the orders of the line or of its sale
        order. It would not find the order, which is linked to the sale order
        line that sold the recurring order, and to no sale order.
        """
        order = self.fsm_order_id
        if order and not order.sale_id and order.sale_line_id:
            return [("id", "=", order.id)]
        return super()._get_invoiceable_fsm_order_domain()
