# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    show_partial_delivery_button = fields.Boolean(
        compute="_compute_partial_delivery_button_visibility", store=False
    )

    def _compute_partial_delivery_button_visibility(self):
        for order in self:
            order.show_partial_delivery_button = order._is_valid_fsm_order(
                order
            ) and any(
                picking.state not in ["done", "cancel"] for picking in order.picking_ids
            )
