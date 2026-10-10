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
            if order.warehouse_id:
                res["warehouse_id"] = order.warehouse_id.id
        return res

    def action_confirm(self):
        """Create a waiting delivery for the requested parts.

        Runs with sudo on stock documents by design: field technicians are
        usually not inventory users — they request the parts, the warehouse
        team reserves and delivers the picking created here.
        """
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Add at least one part to consume."))
        order = self.order_id
        warehouse = self.warehouse_id
        if not warehouse.out_type_id or not warehouse.lot_stock_id:
            raise UserError(
                _("Warehouse has no delivery operation type or stock location.")
            )
        src = warehouse.lot_stock_id
        dest = order.location_id.inventory_location_id or self.env.ref(
            "stock.stock_location_customers"
        )
        partner = order.location_id.partner_id if order.location_id else False
        # picking.fsm_order_id is related to group_id.fsm_order_id: link the
        # delivery to the order through its procurement group.
        group = order.procurement_group_id
        if not group or group.fsm_order_id != order:
            group = (
                self.env["procurement.group"]
                .sudo()
                .create({"name": order.name, "fsm_order_id": order.id})
            )
            order.sudo().procurement_group_id = group.id
        picking = (
            self.env["stock.picking"]
            .sudo()
            .create(
                {
                    "picking_type_id": warehouse.out_type_id.id,
                    "location_id": src.id,
                    "location_dest_id": dest.id,
                    "origin": order.name,
                    "group_id": group.id,
                    "partner_id": partner.id if partner else False,
                }
            )
        )
        move_model = self.env["stock.move"].sudo()
        for line in self.line_ids:
            move_model.create(
                {
                    "name": line.product_id.display_name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_qty,
                    "product_uom": line.product_uom_id.id,
                    "picking_id": picking.id,
                    "location_id": src.id,
                    "location_dest_id": dest.id,
                    "group_id": group.id,
                }
            )
        picking.action_confirm()
        return {
            "type": "ir.actions.act_window",
            "name": _("Parts Delivery"),
            "res_model": "stock.picking",
            "res_id": picking.id,
            "view_mode": "form",
            "target": "current",
        }


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
    product_uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.product_uom_id = line.product_id.uom_id.id
