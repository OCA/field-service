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
        data = self.env["fsm.order"]._read_group(
            [("agreement_id", "in", self.ids)],
            ["agreement_id"],
            ["__count"],
        )
        counts = {rec.id: count for rec, count in data}
        for rec in self:
            rec.service_order_count = counts.get(rec.id, 0)

    def _compute_equipment_count(self):
        data = self.env["fsm.equipment"]._read_group(
            [("agreement_id", "in", self.ids)],
            ["agreement_id"],
            ["__count"],
        )
        counts = {rec.id: count for rec, count in data}
        for rec in self:
            rec.equipment_count = counts.get(rec.id, 0)

    def action_view_service_order(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        orders = self.env["fsm.order"].search([("agreement_id", "in", self.ids)])
        if len(orders) == 1:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = orders.id
        else:
            action["domain"] = [("id", "in", orders.ids)]
        return action

    def action_view_fsm_equipment(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_equipment"
        )
        equipments = self.env["fsm.equipment"].search(
            [("agreement_id", "in", self.ids)]
        )
        if len(equipments) == 1:
            action["views"] = [
                (self.env.ref("fieldservice.fsm_equipment_form_view").id, "form")
            ]
            action["res_id"] = equipments.id
        else:
            action["domain"] = [("id", "in", equipments.ids)]
        return action
