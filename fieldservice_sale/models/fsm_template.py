# Copyright 2022 Elego Software Solutions GmbH
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class FSMTemplate(models.Model):
    _inherit = "fsm.template"

    product_id = fields.Many2one("product.template", string="Product")
