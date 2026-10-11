# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def action_complete(self):
        res = super().action_complete()
        self._carry_over_preventive_lines()
        return res

    def _carry_over_preventive_lines(self):
        """What was not done goes on top of the next open visit."""
        for order in self.filtered("fsm_recurring_id.is_preventive"):
            next_order = self.search(
                [
                    ("fsm_recurring_id", "=", order.fsm_recurring_id.id),
                    ("stage_id.is_closed", "=", False),
                    ("scheduled_date_start", ">", order.scheduled_date_start),
                ],
                order="scheduled_date_start",
                limit=1,
            )
            missed = (
                order.equipment_line_ids.filtered(
                    lambda line: line.state == "pending"
                ).preventive_id
                - next_order.equipment_line_ids.preventive_id
            )
            if next_order and missed:
                next_order.equipment_line_ids = [
                    Command.create(
                        {
                            "equipment_id": preventive.equipment_id.id,
                            "preventive_id": preventive.id,
                            "template_id": preventive.template_id.id,
                            "sequence": 0,
                        }
                    )
                    for preventive in missed
                ]
