# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    repair_id = fields.Many2one("repair.order", string="Repair Order")

    def _create_linked_repair_order(self):
        self.ensure_one()
        if self.equipment_id and self.equipment_id.current_stock_location_id:
            equipment = self.equipment_id
            repair_id = self.env["repair.order"].create(
                {
                    "name": self.name or "",
                    "product_id": equipment.product_id.id or False,
                    "product_uom": equipment.product_id.uom_id.id or False,
                    "location_id": equipment.current_stock_location_id
                    and equipment.current_stock_location_id.id
                    or False,
                    "lot_id": equipment.lot_id.id or "",
                    "product_qty": 1,
                    "internal_notes": self.description,
                    "partner_id": self.location_id.partner_id
                    and self.location_id.partner_id.id
                    or False,
                }
            )
            self.repair_id = repair_id
        elif not self.equipment_id.current_stock_location_id:
            raise ValidationError(
                _(
                    "Cannot create Repair Order because "
                    "Equipment does not have a Current "
                    "Inventory Location."
                )
            )

    @api.model
    def create(self, vals):
        # if FSM order with type repair is created then
        # create a repair order
        order = super().create(vals)
        if order.type.internal_type == "repair":
            order._create_linked_repair_order()
        return order

    def write(self, vals):
        res = super().write(vals)
        if vals.get("type"):
            for order in self:
                # If internal_type is changed to not repair
                # then cancel the repair order
                if order.repair_id and order.internal_type != "repair":
                    order.repair_id.action_repair_cancel()
                    order.repair_id = False
                # If internal_type is changed to repair
                # then create a repair order
                if not order.repair_id and order.internal_type == "repair":
                    order._create_linked_repair_order()
        return res

    @api.onchange("internal_type")
    def _onchange_internal_type(self):
        # If we change the type of the order to not repair,
        # we should inform the user that the repair order will be canceled.
        if self.repair_id and self.internal_type != "repair":
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("The repair order will be cancelled."),
                }
            }
