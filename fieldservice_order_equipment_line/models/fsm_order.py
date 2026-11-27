# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    equipment_line_ids = fields.One2many(
        "fsm.order.equipment.line", "order_id", string="Equipment Checklist"
    )
    checklist_equipment_ids = fields.Many2many(
        "fsm.equipment",
        "fsm_order_checklist_equipment_rel",
        "order_id",
        "equipment_id",
        string="Equipments Added by the Checklist",
        readonly=True,
        copy=False,
        help="Equipments the checklist added to the order. Only these are "
        "removed from the order with their last checklist line.",
    )
    equipment_line_pending_count = fields.Integer(
        string="Pending Checklist Lines",
        compute="_compute_equipment_line_pending_count",
    )

    @api.depends("equipment_line_ids.state")
    def _compute_equipment_line_pending_count(self):
        for order in self:
            order.equipment_line_pending_count = len(
                order.equipment_line_ids.filtered(lambda line: line.state == "pending")
            )
