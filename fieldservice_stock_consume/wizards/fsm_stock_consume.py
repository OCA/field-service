# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FsmStockConsume(models.TransientModel):
    _name = "fsm.stock.consume"
    _description = "Consume Parts from Stock (FSM order)"

    order_id = fields.Many2one("fsm.order", string="Field Service Order", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    line_ids = fields.One2many("fsm.stock.consume.line", "wizard_id", string="Parts")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get("active_id")
        if order_id and self.env.context.get("active_model") == "fsm.order":
            order = self.env["fsm.order"].browse(order_id)
            res["order_id"] = order.id
            warehouse = order.sudo().warehouse_id
            if warehouse:
                res["warehouse_id"] = warehouse.id
        return res

    def _get_source_location(self):
        return self.warehouse_id.lot_stock_id

    def _get_destination_location(self):
        return self.order_id.location_id.inventory_location_id or self.env.ref(
            "stock.stock_location_customers"
        )

    def action_confirm(self):
        """Create a waiting delivery for the requested parts.

        Field technicians are usually not inventory users: they request the
        parts and the warehouse team reserves and delivers the picking, so the
        stock documents are read and created with sudo.
        """
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Add at least one part to consume."))
        picking = self.sudo()._create_delivery()
        return {
            "type": "ir.actions.act_window",
            "name": _("Parts Delivery"),
            "res_model": "stock.picking",
            "res_id": picking.id,
            "view_mode": "form",
            "target": "current",
        }

    def _create_delivery(self):
        order = self.order_id
        picking_type = self.warehouse_id.out_type_id
        src = self._get_source_location()
        if not picking_type or not src:
            raise UserError(
                _("Warehouse has no delivery operation type or stock location.")
            )
        dest = self._get_destination_location()
        # picking.fsm_order_id is related to group_id.fsm_order_id: link the
        # delivery to the order through its procurement group.
        group = order.procurement_group_id
        if group.fsm_order_id != order:
            group = self.env["procurement.group"].create(
                {"name": order.name, "fsm_order_id": order.id}
            )
            order.procurement_group_id = group
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "origin": order.name,
                "group_id": group.id,
                "partner_id": order.location_id.partner_id.id,
                "move_ids": [
                    fields.Command.create(
                        {
                            "name": line.product_id.display_name,
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.product_qty,
                            "product_uom": line.product_uom_id.id,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                            "group_id": group.id,
                            "fsm_order_id": order.id,
                        }
                    )
                    for line in self.line_ids
                ],
            }
        )
        picking.action_confirm()
        return picking


class FsmStockConsumeLine(models.TransientModel):
    _name = "fsm.stock.consume.line"
    _description = "Consume Parts from Stock line"

    wizard_id = fields.Many2one("fsm.stock.consume", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Part",
        required=True,
        domain=[("type", "=", "consu")],
    )
    product_qty = fields.Float(string="Quantity", default=1.0, required=True)
    product_uom_id = fields.Many2one("uom.uom", string="Unit of Measure", required=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.product_uom_id = line.product_id.uom_id.id
