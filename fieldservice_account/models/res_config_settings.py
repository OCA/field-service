# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fsm_filter_location_by_customer = fields.Boolean(
        string='Filter Location with Customer',
        related='company_id.fsm_filter_location_by_customer',
        readonly=False
    )

    fsm_filter_customer_by_location = fields.Boolean(
        string='Filter Customer with Location',
        related='company_id.fsm_filter_customer_by_location',
        readonly=False
    )
