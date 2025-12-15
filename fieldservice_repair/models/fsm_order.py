# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import clean_context


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    repair_ids = fields.One2many(
        "repair.order", "fsm_order_id", string="Repair Orders", readonly=True
    )
    repair_count = fields.Integer(
        string="Repair Orders Count", compute="_compute_repair_count", store=True
    )

    @api.depends("repair_ids")
    def _compute_repair_count(self):
        for order in self:
            order.repair_count = len(order.repair_ids)

    def action_view_repairs(self):
        if self.repair_ids:
            action = {
                "res_model": "repair.order",
                "type": "ir.actions.act_window",
            }
            if len(self.repair_ids) == 1:
                action.update(
                    {
                        "view_mode": "form",
                        "res_id": self.repair_ids[0].id,
                    }
                )
            else:
                action.update(
                    {
                        "name": self.env._("Repair Orders"),
                        "view_mode": "list,form",
                        "domain": [("id", "in", self.repair_ids.ids)],
                    }
                )
            return action

    def _prepare_repair_order_vals(self, equipment):
        """Prepare the values for the repair order for a given equipment."""
        self.ensure_one()
        return {
            "name": f"{self.name} - {equipment.name}",
            "product_id": equipment.product_id.id,
            "product_uom": equipment.product_id.uom_id.id,
            "location_id": equipment.current_stock_location_id.id,
            "lot_id": equipment.lot_id.id,
            "product_qty": 1,
            "internal_notes": self.description,
            "partner_id": self.location_id.partner_id.id,
            "fsm_order_id": self.id,
        }

    def _create_repair_orders(self):
        """Create the repair orders for the FSM orders that have a type of repair."""
        repair_order_vals_list = []
        for rec in self:
            if rec.internal_type != "repair":
                continue
            if rec.repair_ids:
                continue
            if not rec.equipment_ids:
                raise ValidationError(
                    self.env._("Equipments must be set to create Repair Orders.")
                )
            for equipment in rec.equipment_ids:
                if not equipment.current_stock_location_id:
                    raise ValidationError(
                        self.env._(
                            "Cannot create the Repair Order because the Equipment '%s' "
                            "does not have a Current Inventory Location set.",
                            equipment.name,
                        )
                    )
                repair_order_vals = rec._prepare_repair_order_vals(equipment)
                repair_order_vals_list.append(repair_order_vals)
        # pylint: disable=context-overridden
        return (
            self.env["repair.order"]
            .with_context(clean_context(self.env.context))
            .create(repair_order_vals_list)
        )

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to create repair orders if an FSM order with type repair is created
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
                self.repair_ids.action_repair_cancel()
                self.repair_ids = False
            # If the internal type is changed to a repair order, create them
            elif fsm_order_type.internal_type == "repair":
                self._create_repair_orders()
        return res

    @api.onchange("internal_type")
    def _onchange_internal_type(self):
        # If we change the type of the order to not repair,
        # we should inform the user that the repair order will be canceled.
        if self.repair_ids and self.internal_type != "repair":
            return {
                "warning": {
                    "title": self.env._("Warning"),
                    "message": self.env._("The repair orders will be cancelled."),
                }
            }
