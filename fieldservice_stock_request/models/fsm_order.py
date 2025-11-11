# Copyright (C) 2021 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

REQUEST_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("open", "In progress"),
    ("done", "Done"),
    ("cancel", "Cancelled"),
]


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    stock_request_ids = fields.One2many(
        "stock.request", "fsm_order_id", string="Order Lines"
    )
    request_stage = fields.Selection(
        REQUEST_STATES,
        string="Request State",
        default="draft",
    )

    @api.onchange("warehouse_id")
    def _onchange_warehouse_id(self):
        if (
            self.stage_id == self.env.ref("fieldservice.fsm_stage_new")
            and self.stock_request_ids
        ):
            self.stock_request_ids[0].order_id.warehouse_id = self.warehouse_id
            self.stock_request_ids[
                0
            ].order_id.location_id = self.warehouse_id.lot_stock_id
            for line in self.stock_request_ids:
                line.location_id = self.warehouse_id.lot_stock_id

    def action_request_submit(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_("Please create a stock request."))
            for line in rec.stock_request_ids:
                if line.state == "draft":
                    if line.order_id:
                        line.order_id.action_submit()
                    else:
                        line.action_submit()
            rec.request_stage = "submitted"

    def action_request_cancel(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_("Please create a stock request."))
            for line in rec.stock_request_ids.filtered(
                lambda x: x.state in ("draft", "open")
            ):
                if line.order_id:
                    line.order_id.action_cancel()
                else:
                    line.action_cancel()
            rec.request_stage = "cancel"

    def action_request_draft(self):
        for rec in self:
            if not rec.stock_request_ids:
                raise UserError(_("Please create a stock request."))
            for line in rec.stock_request_ids.filtered(lambda x: x.state == "cancel"):
                if line.order_id:
                    line.order_id.action_draft()
                else:
                    line.action_draft()
            rec.request_stage = "draft"
