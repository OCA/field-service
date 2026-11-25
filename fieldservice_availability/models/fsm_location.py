# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocationDeliveryScheduleLine(models.Model):
    _name = "fsm.location.delivery.schedule.line"
    _inherit = "fsm.delivery.schedule.line.mixin"
    _description = "FSM Location Delivery Schedule Line"

    location_id = fields.Many2one(
        "fsm.location", string="Location", required=True, ondelete="cascade"
    )


class FSMLocation(models.Model):
    _name = "fsm.location"
    _inherit = ["fsm.location", "fsm.delivery.schedule.mixin"]

    day_ids = fields.Many2many(
        comodel_name="fsm.route.day",
        relation="fsm_location_route_day_rel",
        column1="location_id",
        column2="day_id",
        string="Delivery Days",
        help="Specific operational delivery days for this location. "
        "If empty, inherits the route's delivery days, company defaults, "
        "or system active days.",
    )

    default_schedule_line_ids = fields.One2many(
        "fsm.location.delivery.schedule.line",
        "location_id",
        domain=[("is_seasonal", "=", False)],
        string="Default Day Schedules",
    )

    seasonal_schedule_line_ids = fields.One2many(
        "fsm.location.delivery.schedule.line",
        "location_id",
        domain=[("is_seasonal", "=", True)],
        string="Seasonal Day Schedules",
    )

    def get_allowed_route_days(self):
        """Returns allowed fsm.route.day recordset for location,
        route, company default, or all active days."""
        self.ensure_one()
        if self.day_ids:
            return self.day_ids
        if self.fsm_route_id:
            return self.fsm_route_id.get_allowed_route_days()
        return self.env.company.fsm_default_route_day_ids or self.env[
            "fsm.route.day"
        ].search([])

    def get_delivery_time_ranges(self, target_date=None):
        """Resolves active delivery hours following hierarchy:
        1. Location seasonal schedule active on target_date (day-specific then general)
        2. Location default schedule (day-specific then general)
        3. Route seasonal schedule active on target_date (day-specific then general)
        4. Route default schedule (day-specific then general)
        5. Global fallback schedule
        Returns a tuple of floats: (start_time, end_time)
        """
        self.ensure_one()
        if not target_date:
            target_date = fields.Date.context_today(self)
        else:
            target_date = fields.Date.to_date(target_date)

        # 1 & 2. Location Scope
        loc_hours = self._resolve_delivery_hours(target_date)
        if loc_hours:
            return loc_hours

        # 3 & 4. Route Scope
        if self.fsm_route_id:
            route_hours = self.fsm_route_id._resolve_delivery_hours(target_date)
            if route_hours:
                return route_hours

        # 5. Global Fallback Scope
        global_range = self.env["fsm.delivery.time.range"].search(
            [], order="sequence asc, id asc", limit=1
        )
        if global_range:
            return global_range.start_time, global_range.end_time

        return 7.0, 15.0
