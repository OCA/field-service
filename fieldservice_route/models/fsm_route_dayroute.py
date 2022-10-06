# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class FSMRouteDayRoute(models.Model):
    _name = "fsm.route.dayroute"
    _description = "Field Service Route Dayroute"

    name = fields.Char(required=True, copy=False, default=lambda self: _("New"))
    person_id = fields.Many2one(comodel_name="fsm.person", string="Person")
    route_id = fields.Many2one(comodel_name="fsm.route", string="Route")
    date = fields.Date(required=True)
    team_id = fields.Many2one(
        comodel_name="fsm.team",
        string="Team",
        default=lambda self: self._default_team_id(),
    )
    stage_id = fields.Many2one(
        comodel_name="fsm.stage",
        string="Stage",
        domain="[('stage_type', '=', 'route')]",
        index=True,
        copy=False,
        default=lambda self: self._default_stage_id(),
    )
    longitude = fields.Float()
    latitude = fields.Float()
    last_location_id = fields.Many2one(
        comodel_name="fsm.location", string="Last Location"
    )
    date_start_planned = fields.Datetime(string="Planned Start Time")
    start_location_id = fields.Many2one(
        comodel_name="fsm.location", string="Start Location"
    )
    end_location_id = fields.Many2one(
        comodel_name="fsm.location", string="End Location"
    )
    work_time = fields.Float(string="Time before overtime (in hours)", default=8.0)
    max_allow_time = fields.Float(
        string="Maximal Allowable Time (in hours)", default=10.0
    )
    order_ids = fields.One2many(
        comodel_name="fsm.order", inverse_name="dayroute_id", string="Orders"
    )
    order_count = fields.Integer(
        compute="_compute_order_count", string="Number of Orders", store=True
    )
    order_remaining = fields.Integer(
        compute="_compute_order_count", string="Available Capacity", store=True
    )
    max_order = fields.Integer(
        related="route_id.max_order",
        string="Maximum Capacity",
        store=True,
        help="Maximum numbers of orders that can be added to this day route.",
    )

    def _default_team_id(self):
        teams = self.env["fsm.team"].search(
            [("company_id", "in", (self.env.user.company_id.id, False))],
            order="sequence asc",
            limit=1,
        )
        if teams:
            return teams
        else:
            raise ValidationError(_("You must create a FSM team first."))

    def _default_stage_id(self):
        return self.env["fsm.stage"].search(
            [("stage_type", "=", "route"), ("is_default", "=", True)], limit=1
        )

    @api.depends("route_id", "order_ids")
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.order_remaining = rec.max_order - rec.order_count

    @api.onchange("route_id")
    def _onchange_person(self):
        self.person_id = self.route_id.fsm_person_id.id

    @api.onchange("date")
    def _onchange_date(self):
        if self.date:
            # TODO: Use the worker timezone and working schedule
            self.date_start_planned = datetime.combine(
                self.date, datetime.strptime("8:00:00", "%H:%M:%S").time()
            )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fsm.route.dayroute"
            ) or _("New")
        if not vals.get("date_start_planned", False) and vals.get("date", False):
            # TODO: Use the worker timezone and working schedule
            date = vals.get("date")
            if type(vals.get("date")) == str:
                date = datetime.strptime(
                    vals.get("date"), DEFAULT_SERVER_DATE_FORMAT
                ).date()
            vals.update(
                {
                    "date_start_planned": datetime.combine(
                        date, datetime.strptime("8:00:00", "%H:%M:%S").time()
                    )
                }
            )
        return super().create(vals)

    @api.constrains("date", "route_id")
    def check_day(self):
        for rec in self:
            if rec.date and rec.route_id:
                # Get the day of the week: Monday -> 0, Sunday -> 6
                day_index = rec.date.weekday()
                day = self.env.ref("fieldservice_route.fsm_route_day_" + str(day_index))
                if day.id not in rec.route_id.day_ids.ids:
                    raise ValidationError(
                        _("The route %(route_name)s does not run on %(name)s!")
                        % {"route_name": rec.route_id.name, "name": day.name}
                    )

    @api.constrains("route_id", "max_order", "order_count")
    def check_capacity(self):
        for rec in self:
            if rec.route_id and rec.order_count > rec.max_order:
                raise ValidationError(
                    _(
                        "The day route is exceeding the maximum number of "
                        "orders of the route."
                    )
                )
