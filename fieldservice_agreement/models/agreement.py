# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    service_order_count = fields.Integer(
        compute="_compute_service_order_count", string="# Service Orders"
    )
    equipment_count = fields.Integer("# Equipments", compute="_compute_equipment_count")
    fsm_location_id = fields.Many2one("fsm.location", string="FSM Location")

    def _compute_service_order_count(self):
        for agreement in self:
            agreement.service_order_count = self.env["fsm.order"].search_count(
                [("agreement_id", "=", agreement.id)]
            )

    def action_view_service_order(self):
        for agreement in self:
            fsm_order_ids = self.env["fsm.order"].search(
                [("agreement_id", "=", agreement.id)]
            )
            action = self.env.ref("fieldservice.action_fsm_operation_order").read()[0]
            if len(fsm_order_ids) == 1:
                action["views"] = [
                    (self.env.ref("fieldservice.fsm_order_form").id, "form")
                ]
                action["res_id"] = fsm_order_ids.ids[0]
            else:
                action["domain"] = [("id", "in", fsm_order_ids.ids)]
            return action

    def _compute_equipment_count(self):
        for agreement in self:
            agreement.equipment_count = self.env["fsm.equipment"].search_count(
                [("agreement_id", "=", agreement.id)]
            )

    def action_view_fsm_equipment(self):
        for agreement in self:
            equipment_ids = self.env["fsm.equipment"].search(
                [("agreement_id", "=", agreement.id)]
            )
            action = self.env.ref("fieldservice.action_fsm_equipment").read()[0]
            if len(equipment_ids) == 1:
                action["views"] = [
                    (self.env.ref("fieldservice.fsm_equipment_form_view").id, "form")
                ]
                action["res_id"] = equipment_ids.ids[0]
            else:
                action["domain"] = [("id", "in", equipment_ids.ids)]
            return action
