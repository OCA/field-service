# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

DIRECTIONS = [
    ("outgoing", "Outgoing"),
    ("incoming", "Incoming"),
]


class FSMOrderStockLine(models.Model):
    _name = "fsm.order.stock.line"
    _description = "Field Service Order Material Line"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Field Service Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    direction = fields.Selection(
        DIRECTIONS,
        required=True,
        default="outgoing",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('type', 'in', ['product', 'consu'])]",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        default=1.0,
        digits="Product Unit of Measure",
        required=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
    )
    move_id = fields.Many2one(
        "stock.move",
        string="Stock Move",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    picking_id = fields.Many2one(
        "stock.picking",
        string="Transfer",
        related="move_id.picking_id",
        store=True,
    )
    state = fields.Selection(
        related="move_id.state",
        string="Status",
    )

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    def _prepare_stock_move_values(self, picking, location_id, location_dest_id, group):
        """Values for the stock.move created to fulfill this material line."""
        self.ensure_one()
        return {
            "name": self.product_id.display_name,
            "product_id": self.product_id.id,
            "product_uom_qty": self.product_uom_qty,
            "product_uom": (self.product_uom_id or self.product_id.uom_id).id,
            "location_id": location_id.id,
            "location_dest_id": location_dest_id.id,
            "picking_id": picking.id,
            "picking_type_id": picking.picking_type_id.id,
            "group_id": group.id,
            "fsm_order_id": self.fsm_order_id.id,
            "company_id": picking.company_id.id,
        }
