# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    fsm_order_ids = fields.Many2many(
        "fsm.order",
        "fsm_order_account_payment",
        "payment_id",
        "fsm_order_id",
        string="FSM Orders",
        compute="_compute_fsm_order_ids",
        store=True,
        index=True,
    )
    fsm_order_count = fields.Integer(
        string="FSM Order Count", compute="_compute_fsm_order_count"
    )

    @api.depends("fsm_order_ids")
    def _compute_fsm_order_count(self):
        for payment in self:
            payment.fsm_order_count = len(payment.fsm_order_ids)

    def action_view_fsm_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        if self.fsm_order_count > 1:
            action["domain"] = [("id", "in", self.fsm_order_ids)]
        elif self.fsm_order_ids:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = self.fsm_order_ids[0].id
        return action

    def _compute_fsm_order_ids(self):
        for record in self:
            fsm_orders = record.reconciled_invoice_ids.mapped("fsm_order_ids")
            record.fsm_order_ids = [Command.set(fsm_orders.ids)]
