# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_fsm_team = fields.Boolean(
        string='Manage Teams',
        implied_group='fieldservice.group_fsm_team')
    group_fsm_vehicle = fields.Boolean(
        string='Manage Vehicles',
        implied_group='fieldservice.group_fsm_vehicle')

    module_fieldservice_stock = fields.Boolean(
        sting='Use Odoo Stock Logistics')
