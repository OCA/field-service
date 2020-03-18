# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    fsm_filter_location_by_customer = fields.Boolean(
        string='Filter Location with Customer'
    )

    fsm_filter_customer_by_location = fields.Boolean(
        string='Filter Customer with Location'
    )
