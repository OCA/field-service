# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_fsm_team = fields.Boolean(
        string='Manage Teams',
        implied_group='fieldservice.group_fsm_team')
    group_fsm_category = fields.Boolean(
        string='Manage Categories',
        implied_group='fieldservice.group_fsm_category')
    group_fsm_tag = fields.Boolean(
        string='Manage Tags',
        implied_group='fieldservice.group_fsm_tag')
    group_fsm_equipment = fields.Boolean(
        string='Manage Equipment',
        implied_group='fieldservice.group_fsm_equipment')
    group_fsm_template = fields.Boolean(
        string='Manage Template',
        implied_group='fieldservice.group_fsm_template')
    module_fieldservice_account = fields.Boolean(
        string='Invoice your FSM orders')
    module_fieldservice_agreement = fields.Boolean(
        string='Manage Agreements')
    module_fieldservice_distribution = fields.Boolean(
        string='Manage Distribution')
    module_fieldservice_maintenance = fields.Boolean(
        string='Link FSM orders to maintenance requests')
    module_fieldservice_repair = fields.Boolean(
        string='Link FSM orders to MRP Repair orders')
    module_fieldservice_skill = fields.Boolean(
        string='Manage Skills')
    module_fieldservice_stock = fields.Boolean(
        string='Use Odoo Logistics')
    module_fieldservice_vehicle = fields.Boolean(
        string='Manage Vehicles')
    module_fieldservice_substatus = fields.Boolean(
        string='Manage Sub-Statuses')

    @api.onchange('module_fieldservice_repair')
    def _onchange_module_fieldservice_repair(self):
        if self.module_fieldservice_repair:
            self.group_fsm_equipment = True

    @api.onchange('module_fieldservice_stock')
    def _onchange_module_fieldservice_stock(self):
        if self.module_fieldservice_stock:
            self.group_stock_production_lot = True
