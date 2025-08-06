# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    repair_id = fields.Many2one("repair.order", string="Repair Order", readonly=True)

    def _prepare_repair_order_vals(self):
        """Prepare the values for the repair order."""
        self.ensure_one()
        return {
            "name": self.name,
            "product_id": self.equipment_id.product_id.id,
            "product_uom": self.equipment_id.product_id.uom_id.id,
            "location_id": self.equipment_id.current_stock_location_id.id,
            "lot_id": self.equipment_id.lot_id.id,
            "product_qty": 1,
            "internal_notes": self.description,
            "partner_id": self.location_id.partner_id.id,
        }

    def _create_repair_orders(self):
        """Create the repair orders for the FSM orders that have a type of repair."""
        created_repair_orders = self.env["repair.order"]
        for rec in self:
            if rec.internal_type != "repair":
                continue
            if rec.repair_id:
                continue
            if not rec.equipment_id:
                raise ValidationError(
                    self.env._("The Equipment must be set to create a Repair Order.")
                )
            if not rec.equipment_id.current_stock_location_id:
                raise ValidationError(
                    self.env._(
                        "Cannot create the Repair Order because the Equipment '%s' "
                        "does not have a Current Inventory Location set.",
                        rec.equipment_id.name,
                    )
                )
            repair_order_vals = rec._prepare_repair_order_vals()
            repair_order = self.env["repair.order"].create(repair_order_vals)
            rec.repair_id = repair_order
            created_repair_orders += repair_order
        return created_repair_orders

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to create a repair.order if an FSM order with type repair is created
        orders = super().create(vals_list)
        orders._create_repair_orders()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if vals.get("type"):
            fsm_order_type = self.env["fsm.order.type"].browse(vals["type"])
            # If internal type is changed to something other than repair,
            # cancel the repair orders
            if fsm_order_type.internal_type != "repair":
                self.repair_id.action_repair_cancel()
                self.repair_id = False
            # If the internal type is changed to a repair order, create them
            elif fsm_order_type.internal_type == "repair":
                self._create_repair_orders()
        return res

    @api.onchange("internal_type")
    def _onchange_internal_type(self):
        # If we change the type of the order to not repair,
        # we should inform the user that the repair order will be canceled.
        if self.repair_id and self.internal_type != "repair":
            return {
                "warning": {
                    "title": self.env._("Warning"),
                    "message": self.env._("The repair order will be cancelled."),
                }
            }
