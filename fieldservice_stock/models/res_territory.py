# Copyright (C) 2019 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResTerritory(models.Model):
    _inherit = "res.territory"

    warehouse_id = fields.Many2one("stock.warehouse")
