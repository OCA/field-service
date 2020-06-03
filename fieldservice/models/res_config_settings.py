# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Groups
    group_fsm_team = fields.Boolean(
        string="Manage Teams", implied_group="fieldservice.group_fsm_team"
    )
    group_fsm_category = fields.Boolean(
        string="Manage Categories", implied_group="fieldservice.group_fsm_category"
    )
    group_fsm_tag = fields.Boolean(
        string="Manage Tags", implied_group="fieldservice.group_fsm_tag"
    )
    group_fsm_equipment = fields.Boolean(
        string="Manage Equipment", implied_group="fieldservice.group_fsm_equipment"
    )
    group_fsm_template = fields.Boolean(
        string="Manage Template", implied_group="fieldservice.group_fsm_template"
    )

    # Modules
    module_fieldservice_account = fields.Boolean(string="Invoice your FSM orders")
    module_fieldservice_activity = fields.Boolean(string="Manage FSM Activities")
    module_fieldservice_agreement = fields.Boolean(string="Manage Agreements")
    module_fieldservice_change_management = fields.Boolean(string="Change Management")
    module_fieldservice_crm = fields.Boolean(string="CRM")
    module_fieldservice_distribution = fields.Boolean(string="Manage Distribution")
    module_fieldservice_fleet = fields.Boolean(
        string="Link FSM vehicles to Fleet vehicles"
    )
    module_fieldservice_geoengine = fields.Boolean(string="Use GeoEngine")
    module_fieldservice_google_map = fields.Boolean(
        string="Allow Field Service Google Map"
    )
    module_fieldservice_location_builder = fields.Boolean(
        string="Use FSM Location Builder"
    )
    module_fieldservice_maintenance = fields.Boolean(
        string="Link FSM orders to maintenance requests"
    )
    module_fieldservice_project = fields.Boolean(string="Projects and Tasks")
    module_fieldservice_purchase = fields.Boolean(
        string="Manage subcontractors and their pricelists"
    )
    module_fieldservice_recurring = fields.Boolean(string="Manage Recurring Orders")
    module_fieldservice_repair = fields.Boolean(
        string="Link FSM orders to MRP Repair orders"
    )
    module_fieldservice_route = fields.Boolean(string="Manage routes")
    module_fieldservice_route_account = fields.Boolean(
        string="Check the amount collected during the route"
    )
    module_fieldservice_route_stock = fields.Boolean(
        string="Check the inventory of the vehicle at the end of the route"
    )
    module_fieldservice_sale = fields.Boolean(string="Sell FSM orders")
    module_fieldservice_size = fields.Boolean(
        string="Manage sizes for orders and locations"
    )
    module_fieldservice_skill = fields.Boolean(string="Manage Skills")
    module_fieldservice_stock = fields.Boolean(string="Use Odoo Logistics")
    module_fieldservice_vehicle = fields.Boolean(string="Manage Vehicles")
    module_fieldservice_substatus = fields.Boolean(string="Manage Sub-Statuses")
    module_fieldservice_web_timeline_view = fields.Boolean(
        string="Allow Field Service Web Timeline View"
    )

    # Companies
    auto_populate_persons_on_location = fields.Boolean(
        string="Auto-populate Workers on Location based on Territory",
        related="company_id.auto_populate_persons_on_location",
        readonly=False,
    )
    auto_populate_equipments_on_order = fields.Boolean(
        string="Auto-populate equipments on Order based on the Location",
        related="company_id.auto_populate_equipments_on_order",
        readonly=False,
    )
    search_on_complete_name = fields.Boolean(
        string="Search Location By Hierarchy",
        related="company_id.search_on_complete_name",
        readonly=False,
    )

    # Dependencies
    @api.onchange("group_fsm_equipment")
    def _onchange_group_fsm_equipment(self):
        if not self.group_fsm_equipment:
            self.auto_populate_the_equipments = False

    @api.onchange("module_fieldservice_repair")
    def _onchange_module_fieldservice_repair(self):
        if self.module_fieldservice_repair:
            self.group_fsm_equipment = True

    @api.onchange("module_fieldservice_stock")
    def _onchange_module_fieldservice_stock(self):
        if self.module_fieldservice_stock:
            self.group_stock_production_lot = True
            self.group_stock_request_order = True

    @api.onchange("module_fieldservice_purchase")
    def _onchange_module_fieldservice_purchase(self):
        if self.module_fieldservice_purchase:
            self.group_manage_vendor_price = True
