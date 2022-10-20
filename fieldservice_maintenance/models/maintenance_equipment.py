# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    is_fsm_equipment = fields.Boolean(string='Is a FSM Equipment')
    product_id = fields.Many2one('product.product', 'Product')
