# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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

    def action_create_fsm_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        action["context"] = {
            "default_opportunity_id": self.id,
            "default_location_id": self.fsm_location_id.id,
            "default_description": self.description,
            "default_priority": self.priority,
        }
        view = self.env.ref("fieldservice.fsm_order_form", raise_if_not_found=False)
        action["views"] = [(view and view.id or False, "form")]
        return action
