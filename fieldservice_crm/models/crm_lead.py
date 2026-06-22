# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    fsm_order_ids = fields.One2many(
        "fsm.order", "opportunity_id", string="Service Orders"
    )
    fsm_location_id = fields.Many2one("fsm.location", string="FSM Location")
    fsm_order_count = fields.Integer(
        compute="_compute_fsm_order_count", string="# FSM Orders"
    )

    def _compute_fsm_order_count(self):
        for rec in self:
            rec.fsm_order_count = len(rec.fsm_order_ids)

    def create_fsm_order(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("Please select a customer."))

        # If not location is selected use the partner's location
        if not self.fsm_location_id:
            if not self.partner_id.fsm_location:
                self.env["fsm.wizard"].action_convert_location(self.partner_id)
            self.fsm_location_id = self.partner_id.fsm_location_id

        return {
            "name": _("Create FSM Order"),
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_opportunity_id": self.id,
                "default_location_id": self.fsm_location_id.id,
            },
        }
