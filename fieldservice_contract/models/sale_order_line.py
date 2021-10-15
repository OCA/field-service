# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Commercial Entity",
        related="order_partner_id.commercial_partner_id",
        store=True,
        index=True,
    )
    fsm_location_id = fields.Many2one(
        string="FSM Location",
        comodel_name="fsm.location",
        copy=True,
        default=lambda x: x.order_id.fsm_location_id,
        domain="[('company_id', 'in', (False, company_id)),"
                "('commercial_partner_id', '=', commercial_partner_id)]"
    )

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        self.ensure_one()
        contract.fsm_location_id = self.order_id.fsm_location_id
        res = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id
        )
        res["fsm_frequency_set_id"] = self.fsm_frequency_set_id.id
        res["fsm_location_id"] = self.fsm_location_id.id or self.order_id.fsm_location_id.id
        return res

    def _field_create_fsm_recurring(self):
        if self.is_contract:
            # we do nothing; it s the contract
            # that will create the order
            return {self.id: None}
        else:
            return super()._field_create_fsm_recurring()

    def _field_create_fsm_order(self):
        if self.is_contract:
            # we do nothing; it s the contract
            # that will create the order
            return {self.id: None}
        else:
            return super()._field_create_fsm_order()
