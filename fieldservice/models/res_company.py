# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_populate_persons_on_location = fields.Boolean(
        string='Auto-populate Workers on Location based on Territory')
    auto_populate_equipments_on_order = fields.Boolean(
        string='Auto-populate Equipments on Order based on Location')
    search_on_complete_name = fields.Boolean(
        string='Search Location By Hierarchy'
    )
