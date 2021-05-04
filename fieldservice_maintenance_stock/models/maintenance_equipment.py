# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    product_id = fields.Many2one("product.product")
    lot_id = fields.Many2one("stock.production.lot", "Product Serial Number")
