# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrderReportMixin(models.AbstractModel):
    _name = "fsm.order.report.mixin"
    _description = "Field Service Order Report Mixin"

    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, required=True
    )
    vehicle_id = fields.Many2one(
        comodel_name="fsm.vehicle",
        string="Vehicle",
        index=True,
        compute="_compute_vehicle_id",
        precompute=True,
        store=True,
        readonly=False,
    )
    dayroute_id = fields.Many2one(
        comodel_name="fsm.route.dayroute", string="Day Route", index=True
    )
    fsm_route_id = fields.Many2one(
        comodel_name="fsm.route",
        string="Route",
        index=True,
        compute="_compute_route_id",
        precompute=True,
        store=True,
        readonly=False,
    )
    person_id = fields.Many2one(
        comodel_name="fsm.person",
        string="Assigned To",
        index=True,
        compute="_compute_person_id",
        precompute=True,
        store=True,
        readonly=False,
    )
    location_id = fields.Many2one("fsm.location", string="Location", index=True)
    stage_id = fields.Many2one(
        "fsm.stage", string="Stage", index=True, domain="[('stage_type', '=', 'order')]"
    )
    tag_ids = fields.Many2many("fsm.tag", string="Tags")
    team_id = fields.Many2one(
        "fsm.team",
        string="Team",
        index=True,
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    type = fields.Many2one("fsm.order.type")
    field_ids = fields.Many2many(
        "ir.model.fields", domain="[('model', '=', 'fsm.order')]", string="Fields"
    )

    @api.depends("location_id")
    def _compute_route_id(self):
        for item in self.filtered("location_id"):
            item.fsm_route_id = item.location_id.fsm_route_id

    @api.depends("fsm_route_id")
    def _compute_person_id(self):
        for item in self.filtered("fsm_route_id"):
            item.person_id = item.fsm_route_id.fsm_person_id

    @api.depends("person_id")
    def _compute_vehicle_id(self):
        for item in self.filtered("person_id"):
            item.vehicle_id = item.person_id.vehicle_id
