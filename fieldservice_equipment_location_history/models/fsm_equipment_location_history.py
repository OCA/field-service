# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FsmEquipmentLocationHistory(models.Model):
    _name = "fsm.equipment.location.history"
    _description = "Equipment Stock Location History"
    _order = "date desc, id desc"

    from_location_id = fields.Many2one(
        "stock.location", string="From Location", required=True
    )
    to_location_id = fields.Many2one(
        "stock.location", string="To Location", required=True
    )
    equipment_id = fields.Many2one("fsm.equipment", string="Equipment", required=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    type_selection = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        string="Type",
        required=True,
        default="inbound",
    )
    picking_id = fields.Many2one(
        "stock.picking", string="Transfer", readonly=True, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        histories = super().create(vals_list)
        for history in histories:
            history._execute_transfer()
        return histories

    def _execute_transfer(self):
        """Move the equipment's serial to the target location with a real
        internal transfer, so quants and traceability stay consistent."""
        self.ensure_one()
        equipment = self.equipment_id
        if not equipment.lot_id or not equipment.product_id:
            raise UserError(
                _(
                    "Equipment %s has no product/serial number: "
                    "a stock transfer cannot be created."
                )
                % equipment.display_name
            )
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "internal")], limit=1
        )
        if not picking_type:
            raise UserError(
                _(
                    "No internal transfer operation type found. "
                    "Enable Storage Locations in Inventory settings."
                )
            )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.from_location_id.id,
                "location_dest_id": self.to_location_id.id,
                "scheduled_date": self.date,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": equipment.display_name,
                "product_id": equipment.product_id.id,
                "product_uom": equipment.product_id.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.from_location_id.id,
                "location_dest_id": self.to_location_id.id,
                "picking_id": picking.id,
                "date": self.date,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move_line = move.move_line_ids[:1]
        if not move_line:
            move_line = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": equipment.product_id.id,
                    "location_id": self.from_location_id.id,
                    "location_dest_id": self.to_location_id.id,
                }
            )
        move_line.write({"lot_id": equipment.lot_id.id, "quantity": 1.0})
        move.picked = True
        picking.button_validate()
        self.picking_id = picking.id
        self._update_equipment_fsm_location()

    def _update_equipment_fsm_location(self):
        """Point the equipment to the FSM location matching the target stock
        location, when one exists (by inventory location, then by name)."""
        self.ensure_one()
        fsm_location = self.env["fsm.location"].search(
            [("inventory_location_id", "=", self.to_location_id.id)], limit=1
        ) or self.env["fsm.location"].search(
            [("name", "=", self.to_location_id.name)], limit=1
        )
        if fsm_location:
            self.equipment_id.location_id = fsm_location.id
