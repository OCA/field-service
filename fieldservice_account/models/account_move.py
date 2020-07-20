# Copyright (C) 2018, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fsm_order_ids = fields.Many2many(
        "fsm.order",
        "fsm_order_account_move_rel",
        "invoice_id",
        "fsm_order_id",
        string="FSM Orders",
    )
    fsm_order_count = fields.Integer(
        string="FSM Order Count", compute="_compute_fsm_order_count", readonly=True
    )

    @api.depends("fsm_order_ids")
    def _compute_fsm_order_count(self):
        for invoice in self:
            invoice.fsm_order_count = len(invoice.fsm_order_ids)

    def action_view_fsm_orders(self):
        action = self.env.ref("fieldservice.action_fsm_dash_order").read()[0]
        if self.fsm_order_count > 1:
            action["domain"] = [("id", "in", self.fsm_order_ids.ids)]
        elif self.fsm_order_ids:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = self.fsm_order_ids[0].id
        return action
