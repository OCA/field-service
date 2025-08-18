# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _prepare_return_procurement_group_values(self):
        self.ensure_one()
        return {
            "name": self.display_name,
            "fsm_order_id": self.id,
            "move_type": "direct",
        }

    def _get_equipment_current_location(self):
        self.ensure_one()
        if self.equipment_id.current_stock_location_id:
            return self.equipment_id.current_stock_location_id
        elif self.equipment_id.current_location_id:
            return (
                self.equipment_id.current_location_id
                and self.equipment_id.current_location_id.inventory_location_id
            )
        else:
            raise ValidationError(
                _("Impossible to find the equipment current location.")
            )

    def _prepare_return_stock_picking_values(self):
        self.ensure_one()
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
        self.ensure_one()
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

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders.filtered(lambda rec: rec.type.internal_type == "return"):
            if not order.type.picking_type_id or not order.equipment_id:
                raise ValidationError(
                    _(
                        "You must set a Picking Type on the order type "
                        "and an equipment on the order."
                    )
                )
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
        return orders
