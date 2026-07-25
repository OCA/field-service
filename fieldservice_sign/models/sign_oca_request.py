# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SignOcaRequest(models.Model):
    _inherit = "sign.oca.request"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Field Service Order",
        compute="_compute_fsm_order_id",
        readonly=True,
        store=True,
    )

    @api.depends("record_ref")
    def _compute_fsm_order_id(self):
        for request in self:
            if request.record_ref and request.record_ref._name == "fsm.order":
                request.fsm_order_id = request.record_ref.id
            else:
                request.fsm_order_id = False
