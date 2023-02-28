# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _field_service_generate_line_fsm_orders(self, new_fsm_sol):
        """
        Prevent the creation of FSM orders from sale order with associated
        with contract
        """
        new_fsm_sol = new_fsm_sol.filtered(lambda sol: not sol.is_contract)
        return super()._field_service_generate_line_fsm_orders(new_fsm_sol)

    def _field_service_generate_sale_fsm_orders(self, new_fsm_sol):
        """
        Prevent the creation of FSM orders from sale order lines associated
        with contract lines
        """
        new_fsm_sol = new_fsm_sol.filtered(lambda sol: not sol.is_contract)
        return super()._field_service_generate_sale_fsm_orders(new_fsm_sol)
