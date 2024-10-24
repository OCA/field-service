# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _prepare_return_procurement_group_values(self):
        return {
            "name": self.display_name,
            "fsm_order_id": self.id,
            "move_type": "direct",
        }

    def _prepare_return_stock_picking_values(self):
        source_location_id = self._get_equipment_current_location()
        return {
            "picking_type_id": self.type.picking_type_id.id,
            "origin": self.display_name,
            "location_dest_id": self.type.picking_type_id.default_location_dest_id.id,
            "location_id": source_location_id and source_location_id.id,
            "fsm_order_id": self.id,
            "group_id": self.procurement_group_id.id,
        }

    def _prepare_return_stock_move_values(self):
        source_location_id = self._get_equipment_current_location()
        return {
            "name": self.display_name,
            "product_id": self.equipment_id.product_id.id,
            "product_uom_qty": 1,
            "product_uom": self.equipment_id.product_id.uom_id.id,
            "location_id": source_location_id.id,
            "location_dest_id": self.type.picking_type_id.default_location_dest_id.id,
            "group_id": self.procurement_group_id.id,
            "fsm_order_id": self.id,
            "lot_ids": [(4, self.equipment_id.lot_id.id)]
            if self.equipment_id.lot_id
            else False,
        }

    def _get_equipment_current_location(self):
        self.ensure_one()
        if not self.equipment_id:
            raise ValidationError(
                _(
                    "Cannot create Return Order because "
                    "order does not have a current equipment."
                )
            )
        if self.equipment_id.location_id:
            return (
                self.equipment_id.location_id
                and self.equipment_id.location_id.inventory_location_id
            )
        elif self.equipment_id.current_location_id:
            return (
                self.equipment_id.current_location_id
                and self.equipment_id.current_location_id.inventory_location_id
            )
        else:
            raise ValidationError(
                _(
                    "Cannot create Return Order because "
                    "equipment does not have a current location."
                )
            )

    @api.model
    def create(self, vals):
        # if FSM order with type return is created then
        # create a picking order
        order = super().create(vals)
        if order.type.internal_type == "return":
            if order.equipment_id and order.type.picking_type_id:
                group = self.env["procurement.group"].search(
                    [("fsm_order_id", "=", order.id)]
                )
                if not group:
                    values = order._prepare_return_procurement_group_values()
                    group = self.env["procurement.group"].create(values)
                order.procurement_group_id = group and group.id
                return_picking_values = order._prepare_return_stock_picking_values()
                new_picking = self.env["stock.picking"].create(return_picking_values)
                return_move_values = order._prepare_return_stock_move_values()
                return_move_values["picking_id"] = new_picking.id
                self.env["stock.move"].create(return_move_values)
                new_picking.action_confirm()

            elif not order.type.picking_type_id:
                raise ValidationError(
                    _(
                        "Cannot create Return Order because "
                        "order type does not have a current "
                        "Picking Type."
                    )
                )
        return order
