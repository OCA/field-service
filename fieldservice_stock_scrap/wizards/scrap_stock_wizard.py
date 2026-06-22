# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ScrapStockEntryWizard(models.TransientModel):
    _name = "scrap.stock.entry.wizard"
    _description = "Scrap Stock Entry Wizard"

    @api.constrains("scrap_qty")
    def _check_scrap_qty(self):
        for line in self:
            if line.scrap_qty > line.quantity:
                raise ValidationError(
                    _(
                        "Scrap quantity can't be "
                        "more than initial quantity for product %s",
                        line.product_id.name,
                    )
                )

    scrap_stock_id = fields.Many2one("scrap.stock.wizard", "Scrap Stock Wizard")
    product_id = fields.Many2one(
        "product.product",
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True,
    )
    quantity = fields.Float(
        digits="Product Unit of Measure",
        required=True,
        default=1,
    )
    scrap_qty = fields.Float(
        "Scrap Quantity",
        digits="Product Unit of Measure",
        required=True,
        default=0,
    )
    location_id = fields.Many2one(
        "stock.location",
        "Internal Location",
        required=True,
        domain="[('usage','=','internal')]",
    )
    stock_request_id = fields.Many2one(
        "stock.request",
        required=True,
    )


class ScrapStockWizard(models.TransientModel):
    _name = "scrap.stock.wizard"
    _description = "Scrap Stock Wizard"

    @api.model
    def _default_scrap_stock_entries(self):
        scrap_stock_entries = []
        fsm_order = self.env["fsm.order"].browse(self.env.context["fsm_order_id"])
        for stock_request in fsm_order.stock_request_ids.filtered(
            lambda x: x.direction == "inbound"
        ):
            scrap_stock_entries.append(
                self.env["scrap.stock.entry.wizard"]
                .create(
                    {
                        "product_id": stock_request.product_id.id,
                        "quantity": stock_request.product_uom_qty,
                        "location_id": stock_request.location_id.id,
                        "stock_request_id": stock_request.id,
                    }
                )
                .id
            )
        return self.env["scrap.stock.entry.wizard"].browse(scrap_stock_entries)

    scrap_stock_entries = fields.One2many(
        "scrap.stock.entry.wizard",
        "scrap_stock_id",
        "Scrap stock entries",
        default=_default_scrap_stock_entries,
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, required=True
    )
    scrap_location_id = fields.Many2one(
        "stock.location",
        "Scrap Location",
        compute="_compute_scrap_location_id",
        store=True,
        required=True,
        precompute=True,
        domain="[('scrap_location', '=', True)]",
        readonly=False,
    )

    @api.depends("company_id")
    def _compute_scrap_location_id(self):
        groups = self.env["stock.location"]._read_group(
            [("company_id", "in", self.company_id.ids), ("scrap_location", "=", True)],
            ["company_id"],
            ["id:min"],
        )
        locations_per_company = {
            company.id: stock_warehouse_id for company, stock_warehouse_id in groups
        }
        for scrap in self:
            scrap.scrap_location_id = locations_per_company[scrap.company_id.id]

    def scrap(self, product_id, scrap_qty, scrap_id):
        move_id = self.env["stock.move"].create(
            {
                "fsm_order_id": self.env.context["fsm_order_id"],
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref(
                    "fieldservice_stock_scrap.intermediate_location"
                ).id,
                "product_id": product_id.id,
                "picked": True,
                "product_uom_qty": scrap_qty,
                "name": (f"Transfer {scrap_id}-"),
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "company_id": self.company_id.id,
                            "product_id": product_id.id,
                            "quantity": scrap_qty,
                        },
                    )
                ],
            }
        )
        move_id._action_done()
        scrap_id = self.env["stock.scrap"].create(
            {
                "location_id": self.env.ref(
                    "fieldservice_stock_scrap.intermediate_location"
                ).id,
                "scrap_location_id": self.scrap_location_id.id,
                "product_id": product_id.id,
                "scrap_qty": scrap_qty,
                "fsm_order_id": self.env.context["fsm_order_id"],
            }
        )
        scrap_id.move_ids = [(4, move_id.id)]
        scrap_id.action_validate()

    def action_scrap(self):
        self.ensure_one()
        for line in self.scrap_stock_entries.filtered(lambda x: x.scrap_qty > 0):
            self.scrap(line.product_id, line.scrap_qty, line.id)
            if line.stock_request_id.product_uom_qty - line.scrap_qty == 0:
                line.stock_request_id.unlink()
            else:
                line.stock_request_id.product_uom_qty -= line.scrap_qty

        scrap_stock_requests = self.scrap_stock_entries.mapped("stock_request_id")
        fsm_order = self.env["fsm.order"].browse(self.env.context["fsm_order_id"])
        inbound_requests = fsm_order.stock_request_ids.filtered(
            lambda x: x.direction == "inbound"
        )
        unmatched_requests = inbound_requests - scrap_stock_requests

        for request in unmatched_requests:
            self.scrap(
                request.product_id,
                request.product_uom_qty,
                request.id,
            )
            request.unlink()

        orders_to_delete = self.env["stock.request.order"].search(
            [("fsm_order_id", "=", fsm_order.id), ("stock_request_ids", "=", False)]
        )
        orders_to_delete.unlink()
