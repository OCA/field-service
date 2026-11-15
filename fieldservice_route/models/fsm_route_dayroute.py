# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_CALENDAR_DEPENDS = (
    "company_id.tz",
    "attendance_ids.hour_from",
    "attendance_ids.hour_to",
    "attendance_ids.dayofweek",
    "attendance_ids.day_period",
    "attendance_ids.date",
    "attendance_ids.duration_based",
    "attendance_ids.duration_hours",
)


def _calendar_depends(prefix):
    return [f"{prefix}.{field_name}" for field_name in _CALENDAR_DEPENDS]


class FSMRouteDayRoute(models.Model):
    _name = "fsm.route.dayroute"
    _description = "Field Service Route Dayroute"

    name = fields.Char(
        required=True, copy=False, default=lambda self: self.env._("New")
    )
    person_id = fields.Many2one(
        comodel_name="fsm.person",
        compute="_compute_person_id",
        store=True,
        readonly=False,
    )
    route_id = fields.Many2one(comodel_name="fsm.route")
    date = fields.Date(required=True)
    team_id = fields.Many2one(
        comodel_name="fsm.team",
        default=lambda self: self._default_team_id(),
    )
    stage_id = fields.Many2one(
        comodel_name="fsm.stage",
        domain="[('stage_type', '=', 'route')]",
        index=True,
        copy=False,
        default=lambda self: self._default_stage_id(),
    )
    longitude = fields.Float()
    latitude = fields.Float()
    last_location_id = fields.Many2one(comodel_name="fsm.location")
    date_start_planned = fields.Datetime(
        string="Planned Start Time",
        compute="_compute_date_start_planned",
        store=True,
        readonly=False,
    )
    start_location_id = fields.Many2one(comodel_name="fsm.location")
    end_location_id = fields.Many2one(comodel_name="fsm.location")
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
            [("company_id", "in", (self.env.company.id, False))],
            order="sequence asc",
            limit=1,
        )
        if teams:
            return teams
        raise ValidationError(self.env._("You must create a FSM team first."))

    def _default_stage_id(self):
        return self.env["fsm.stage"].search(
            [("stage_type", "=", "route"), ("is_default", "=", True)], limit=1
        )

    @api.model
    def _planned_start_from_date(self, route_date, person=None, route=None, team=None):
        """Return planned start as UTC naive datetime for the given route date."""
        route_date = fields.Date.to_date(route_date)
        if route and not person:
            person = route.fsm_person_id
        company = team.company_id if team else self.env.company
        calendar = (person and person.calendar_id) or company.resource_calendar_id
        tz_name = (
            (person and person.partner_id.tz)
            or (calendar and calendar.company_id.tz)
            or self.env.user.tz
            or "UTC"
        )
        tzinfo = ZoneInfo(tz_name)
        day_start = datetime.combine(route_date, time.min, tzinfo=tzinfo)
        # Localize next midnight so DST transitions get the correct offset.
        day_end = datetime.combine(
            route_date + timedelta(days=1), time.min, tzinfo=tzinfo
        )
        if calendar:
            work_time = calendar._get_closest_work_time(
                day_start,
                match_end=False,
                search_range=(day_start, day_end),
                compute_leaves=False,
            )
            if work_time:
                return work_time.astimezone(UTC).replace(tzinfo=None)
        fallback = datetime.combine(route_date, time(8, 0), tzinfo=tzinfo)
        return fallback.astimezone(UTC).replace(tzinfo=None)

    @api.depends("route_id", "route_id.max_order", "max_order", "order_ids")
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.order_remaining = rec.max_order - rec.order_count

    @api.depends("route_id", "route_id.fsm_person_id")
    def _compute_person_id(self):
        for rec in self:
            if not rec.route_id.fsm_person_id:
                rec.person_id = None
                continue

            rec.person_id = rec.route_id.fsm_person_id

    @api.depends(
        "date",
        "person_id",
        "person_id.partner_id.tz",
        *(_calendar_depends("person_id.calendar_id")),
        "route_id",
        "route_id.fsm_person_id",
        "route_id.fsm_person_id.partner_id.tz",
        *(_calendar_depends("route_id.fsm_person_id.calendar_id")),
        "team_id",
        "team_id.company_id",
        *(_calendar_depends("team_id.company_id.resource_calendar_id")),
    )
    def _compute_date_start_planned(self):
        for rec in self:
            if not rec.date:
                rec.date_start_planned = False
                continue
            rec.date_start_planned = rec._planned_start_from_date(
                rec.date,
                person=rec.person_id or rec.route_id.fsm_person_id,
                route=rec.route_id,
                team=rec.team_id,
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", self.env._("New")) == self.env._("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fsm.route.dayroute"
                ) or self.env._("New")
            if not vals.get("date_start_planned") and vals.get("date"):
                route = (
                    self.env["fsm.route"].browse(vals["route_id"])
                    if vals.get("route_id")
                    else self.env["fsm.route"]
                )
                person = (
                    self.env["fsm.person"].browse(vals["person_id"])
                    if vals.get("person_id")
                    else self.env["fsm.person"]
                )
                if vals.get("team_id"):
                    team = self.env["fsm.team"].browse(vals["team_id"])
                else:
                    team = self._default_team_id()
                    vals["team_id"] = team.id
                vals["date_start_planned"] = self._planned_start_from_date(
                    vals["date"],
                    person=person,
                    route=route,
                    team=team,
                )
        return super().create(vals_list)

    @api.constrains("date", "route_id")
    def check_day(self):
        for rec in self:
            if rec.date and rec.route_id:
                # Get the day of the week: Monday -> 0, Sunday -> 6
                day_index = rec.date.weekday()
                day = self.env.ref("fieldservice_route.fsm_route_day_" + str(day_index))
                if day.id not in rec.route_id.day_ids.ids:
                    raise ValidationError(
                        self.env._(
                            "The route %(route_name)s does not run on %(name)s!",
                            route_name=rec.route_id.name,
                            name=day.name,
                        )
                    )

    @api.constrains("route_id", "max_order", "order_count")
    def check_capacity(self):
        for rec in self:
            if rec.route_id and rec.order_count > rec.max_order:
                raise ValidationError(
                    self.env._(
                        "The day route is exceeding the maximum number of "
                        "orders of the route."
                    )
                )
