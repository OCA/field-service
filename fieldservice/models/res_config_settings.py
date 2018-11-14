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
    group_fsm_category = fields.Boolean(
        string='Manage Categories',
        implied_group='fieldservice.group_fsm_category')
    group_fsm_tag = fields.Boolean(
        string='Manage Tags',
        implied_group='fieldservice.group_fsm_tag')
    group_fsm_equipment = fields.Boolean(
        string='Manage Equipment',
        implied_group='fieldservice.group_fsm_equipment')
    module_fieldservice_agreement = fields.Boolean(
        string='Manage Agreements')
    module_fieldservice_skill = fields.Boolean(
        string='Manage Skills')
    module_fieldservice_stock = fields.Boolean(
        string='Use Odoo Stock Logistics',
        implied_group='fieldservice.group_fsm_vehicle')
