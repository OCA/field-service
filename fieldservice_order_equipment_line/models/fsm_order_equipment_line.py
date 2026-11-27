# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models


class FSMOrderEquipmentLine(models.Model):
    _name = "fsm.order.equipment.line"
    _description = "Field Service Order Equipment Line"
    _order = "order_id, sequence, id"
    _rec_name = "equipment_id"
    _check_company_auto = True

    order_id = fields.Many2one(
        "fsm.order", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    equipment_id = fields.Many2one(
        "fsm.equipment",
        required=True,
        index=True,
        ondelete="restrict",
        check_company=True,
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
        lines._link_order_equipments()
        return lines

    def write(self, vals):
        if not {"equipment_id", "order_id"} & set(vals):
            return super().write(vals)
        previous = [(line.order_id, line.equipment_id) for line in self]
        res = super().write(vals)
        self._link_order_equipments()
        self._unlink_order_equipments(previous)
        return res

    def unlink(self):
        previous = [(line.order_id, line.equipment_id) for line in self]
        res = super().unlink()
        self._unlink_order_equipments(previous)
        return res

    def _link_order_equipments(self):
        for order, lines in self.grouped("order_id").items():
            added = lines.equipment_id - order.equipment_ids
            if added:
                links = [Command.link(equipment.id) for equipment in added]
                order.write({"equipment_ids": links, "checklist_equipment_ids": links})

    @api.model
    def _unlink_order_equipments(self, previous):
        """Remove the equipments the checklist added once no line lists them.

        Equipments added directly to the order are kept.
        """
        for order, equipment in previous:
            if (
                equipment in order.checklist_equipment_ids
                and equipment not in order.equipment_line_ids.equipment_id
            ):
                unlinks = [Command.unlink(equipment.id)]
                order.write(
                    {"equipment_ids": unlinks, "checklist_equipment_ids": unlinks}
                )

    def action_done(self):
        return self.write({"state": "done", "date_done": fields.Datetime.now()})

    def action_not_found(self):
        return self.write({"state": "not_found", "date_done": False})

    def action_pending(self):
        return self.write({"state": "pending", "date_done": False})
