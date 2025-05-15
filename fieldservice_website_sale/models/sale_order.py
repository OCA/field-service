# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_shipping_id", "partner_id", "company_id")
    def onchange_partner_shipping_id(self):
        super().onchange_partner_shipping_id()

        if self.partner_shipping_id.fsm_location_id:
            self.sudo().write(
                {"fsm_location_id": self.partner_shipping_id.fsm_location_id}
            )

        return {}
