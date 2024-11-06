# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        res = super()._compute_duration()
        for rec in self:
            if rec.fsm_stage_history_ids and rec.date_end:
                stage_rec = self.env["fsm.stage.history"].search(
                    [("order_id", "=", rec.id)], order="id desc", limit=1
                )
                rec.duration = stage_rec.total_duration
            elif not rec.date_end:
                rec.duration = 0.0
        return res

    @api.depends("sale_id.transaction_ids.state")
    def _compute_payment_state(self):
        for rec in self:
            payment_state = "not_paid"
            paid_payment_check_list = [
                True if paym.state == "done" else False
                for paym in rec.sale_id.transaction_ids
            ]
            if rec.sale_id.transaction_ids:
                if all(paid_payment_check_list):
                    payment_state = "paid"
                elif rec.sale_id.transaction_ids.filtered(
                    lambda r: r.state == "pending"
                ):
                    payment_state = "pending"
            rec.payment_state = payment_state

    duration = fields.Float(
        string="Actual duration",
        compute=_compute_duration,
        help="Actual duration in hours",
        store=True,
    )
    fsm_stage_history_ids = fields.One2many(
        "fsm.stage.history", "order_id", string="Stage History"
    )
    payment_state = fields.Selection(
        [("not_paid", "Not Paid"), ("paid", "Paid"), ("pending", "Pending")],
        compute="_compute_payment_state",
        store=True,
    )

    @api.model
    def create_fsm_attachment(self, name, datas, res_model, res_id):
        if res_model == "fsm.order":
            attachment = (
                self.env["ir.attachment"]
                .sudo()
                .create(
                    {
                        "name": name,
                        "datas": datas,
                        "res_model": res_model,
                        "res_id": res_id,
                    }
                )
            )
            return attachment.id

    @api.model
    def generate_so_payment_link(self, fsm_order_id):
        order = self.env["fsm.order"].browse(fsm_order_id)
        if not order.sale_id:
            return {
                "payment_status": False,
                "message": "The sale order is not found related to this FSO.",
            }
        payment_link_id = (
            self.env["payment.link.wizard"]
            .with_context(
                default_res_model="sale.order", default_res_id=order.sale_id.id
            )
            .sudo()
            .create(
                {
                    "res_model": "sale.order",
                    "res_id": order.sale_id.id,
                    "amount": order.sale_id.amount_total,
                    "currency_id": order.sale_id.currency_id.id,
                    "partner_id": order.sale_id.partner_id.id,
                    "description": order.sale_id.name,
                }
            )
        )
        return {"payment_status": True, "payment_link": payment_link_id.link}
