# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    size_id = fields.Many2one(
        "fsm.size",
        compute="_compute_size_id",
        precompute=True,
        readonly=False,
        store=True,
    )
    size_value = fields.Float(
        string="Order Size",
        compute="_compute_size_value",
        precompute=True,
        readonly=False,
        store=True,
    )
    size_uom_category = fields.Many2one(
        string="Unit of Measure Category",
        related="size_id.uom_id.category_id",
    )
    size_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=?', size_uom_category)]",
        compute="_compute_size_uom",
        precompute=True,
        readonly=False,
        store=True,
    )

    @api.depends("type")
    def _compute_size_id(self):
        for rec in self:
            if rec.type:
                rec.size_id = self.env["fsm.size"].search(
                    [("type_id", "=", rec.type.id), ("is_order_size", "=", True)],
                    limit=1,
                )

    @api.depends("size_id", "location_id")
    def _compute_size_value(self):
        for rec in self:
            if not rec.size_id or not rec.location_id:
                continue
            size = self.env["fsm.location.size"].search(
                [
                    ("location_id", "=", self.location_id.id),
                    ("size_id", "=", self.size_id.id),
                ],
                limit=1,
            )
            rec.size_value = size.quantity

    @api.depends("size_id")
    def _compute_size_uom(self):
        for rec in self:
            rec.size_uom = rec.size_id.uom_id
