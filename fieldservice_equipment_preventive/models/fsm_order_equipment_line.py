# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMOrderEquipmentLine(models.Model):
    _inherit = "fsm.order.equipment.line"

    preventive_id = fields.Many2one(
        "fsm.equipment.preventive",
        string="Preventive Visit",
        ondelete="set null",
        domain="[('equipment_id', '=', equipment_id)]",
    )
    preventive_type_id = fields.Many2one(
        related="preventive_id.type_id", string="Visit Type", store=True
    )

    def action_done(self):
        res = super().action_done()
        for line in self.filtered("preventive_id"):
            line.preventive_id.last_date = fields.Date.context_today(
                line, line.date_done
            )
        return res
