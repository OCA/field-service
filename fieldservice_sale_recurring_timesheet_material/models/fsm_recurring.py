# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    def action_create_sale_lines(self):
        """Add the timesheets and consumed materials of all the orders of
        the recurring order to the sale order that sold it, in one go.
        """
        self.fsm_order_ids.action_create_sale_lines()
        if len(self) == 1:
            return self.action_view_sales()
        return True
