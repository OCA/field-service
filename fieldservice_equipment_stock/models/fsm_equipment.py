# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    product_id = fields.Many2one("product.product", string="Product")
    lot_id = fields.Many2one("stock.lot", string="Serial #")
    current_stock_location_id = fields.Many2one(
        "stock.location",
        string="Current Inventory Location",
        compute="_compute_current_stock_loc_id",
    )

    @api.depends("product_id", "lot_id")
    def _compute_current_stock_loc_id(self):
        stock_quant_obj = self.env["stock.quant"]
        for equipment in self:
            quants = stock_quant_obj.search(
                [("lot_id", "=", equipment.lot_id.id)], order="id desc", limit=1
            )
            equipment.current_stock_location_id = (
                quants.location_id and quants.location_id.id or False
            )

    @api.onchange("product_id")
    def _onchange_product(self):
        self.current_stock_location_id = False

    @api.model_create_multi
    def create(self, vals_list):
        equipments = super().create(vals_list)
        for equipment in equipments:
            if equipment.lot_id:
                equipment.lot_id.fsm_equipment_id = equipment.id
        return equipments

    def write(self, vals):
        res = super().write(vals)
        for equipment in self:
            if "lot_id" in vals:
                equipment.lot_id.fsm_equipment_id = equipment.id
        return res
