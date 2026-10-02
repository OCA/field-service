# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class FSMOrderEquipmentLine(models.Model):
    _name = "fsm.order.equipment.line"
    _description = "Field Service Order Equipment Line"
    _order = "order_id, sequence, id"
    _rec_name = "equipment_id"

    order_id = fields.Many2one(
        "fsm.order", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    equipment_id = fields.Many2one(
        "fsm.equipment", required=True, index=True, ondelete="restrict"
    )
    current_location_id = fields.Many2one(related="equipment_id.current_location_id")
    sequence = fields.Integer(default=10)
    template_id = fields.Many2one(
        "fsm.template", string="Template", help="Work to perform on the equipment."
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("not_found", "Not Found")],
        default="pending",
        required=True,
    )
    date_done = fields.Datetime(readonly=True)
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for order, order_lines in lines.grouped("order_id").items():
            order.equipment_ids = [
                Command.link(equipment.id) for equipment in order_lines.equipment_id
            ]
        return lines

    def unlink(self):
        orders = self.order_id
        res = super().unlink()
        for order in orders:
            order.equipment_ids = [
                Command.unlink(equipment.id)
                for equipment in order.equipment_ids
                - order.equipment_line_ids.equipment_id
            ]
        return res

    def action_done(self):
        return self.write({"state": "done", "date_done": fields.Datetime.now()})

    def action_not_found(self):
        return self.write({"state": "not_found", "date_done": False})

    def action_pending(self):
        return self.write({"state": "pending", "date_done": False})
