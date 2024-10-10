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

    duration = fields.Float(
        string="Actual duration",
        compute=_compute_duration,
        help="Actual duration in hours",
        store=True,
    )
    fsm_stage_history_ids = fields.One2many(
        "fsm.stage.history", "order_id", string="Stage History"
    )

    @api.model
    def create_fsm_attachment(self, name, datas, res_model, res_id):
        if res_model == "fsm.order":
            attachment = self.env["ir.attachment"].sudo().create({
                "name": name,
                "datas": datas,
                "res_model": res_model,
                "res_id": res_id,
            })
            return attachment.id
