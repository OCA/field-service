# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('map', 'Map')])
