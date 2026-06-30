# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

from pytz import timezone, utc

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    _ROUTE_WRITE_FIELDS = frozenset(
        {
            "person_id",
            "scheduled_date_start",
            "scheduled_date_end",
            "scheduled_duration",
            "location_id",
            "dayroute_id",
            "team_id",
        }
    )

    dayroute_id = fields.Many2one(
        comodel_name="fsm.route.dayroute", string="Day Route", index=True
    )
    fsm_route_id = fields.Many2one(related="location_id.fsm_route_id", string="Route")

    person_id = fields.Many2one(
        comodel_name="fsm.person",
        string="Assigned To",
        index=True,
        compute="_compute_person_id",
        store=True,
        readonly=False,
    )

    @api.depends("fsm_route_id", "fsm_route_id.fsm_person_id")
    def _compute_person_id(self):
        for item in self.filtered("fsm_route_id"):
            item.person_id = item.fsm_route_id.fsm_person_id

    def prepare_dayroute_values(self, values):
        return {
            "person_id": values["person_id"],
            "date": values["date"],
            "route_id": values["route_id"],
            "team_id": values["team_id"],
        }

    def _get_route_id_from_vals(self, vals):
        if vals.get("fsm_route_id"):
            return vals["fsm_route_id"]
        location_id = vals.get("location_id") or self.location_id.id
        if location_id:
            return self.env["fsm.location"].browse(location_id).fsm_route_id.id
        return self.fsm_route_id.id

    def _get_team_id_for_dayroute(self, vals):
        """Resolve the order team so day routes use the correct company calendar."""
        if vals.get("team_id"):
            return vals["team_id"]
        if self and self.team_id:
            return self.team_id.id
        location_id = vals.get("location_id") or (
            self.location_id.id if self else False
        )
        if location_id:
            team = self.env["fsm.location"].browse(location_id).team_id
            if team:
                return team.id
        return self.env["fsm.order"]._default_team_id().id

    def _route_id_changing(self, vals, route_id):
        """True when vals actually change the order's effective route."""
        if "location_id" not in vals and "fsm_route_id" not in vals:
            return False
        return (route_id or False) != (self.fsm_route_id.id or False)

    def _get_person_id_for_dayroute(self, vals, route_id):
        if "person_id" in vals:
            return vals.get("person_id") or False
        # Location/route changes adopt the new route worker (or clear when
        # unstaffed). Reschedules keep a manually assigned worker.
        if self._route_id_changing(vals, route_id):
            if route_id:
                route = self.env["fsm.route"].browse(route_id)
                return route.fsm_person_id.id if route.fsm_person_id else False
            return self.person_id.id or False
        if self.person_id:
            return self.person_id.id
        if route_id:
            route = self.env["fsm.route"].browse(route_id)
            if route.fsm_person_id:
                return route.fsm_person_id.id
        return self.fsm_route_id.fsm_person_id.id

    def _tz_name_for_route_day(self, person=None, route=None):
        person = person or self.env["fsm.person"]
        route = route or self.env["fsm.route"]
        route_person = route.fsm_person_id if route else self.env["fsm.person"]
        return (
            (person.partner_id.tz if person else False)
            or (person.calendar_id.tz if person and person.calendar_id else False)
            or (route_person.partner_id.tz if route_person else False)
            or (
                route_person.calendar_id.tz
                if route_person and route_person.calendar_id
                else False
            )
            or self.env.user.tz
            or "UTC"
        )

    def _local_date_from_scheduled_start(
        self, scheduled_start, person=None, route=None
    ):
        """Return the worker/route local calendar day for a UTC-naive datetime."""
        start = fields.Datetime.to_datetime(scheduled_start)
        if not start:
            return False
        tzinfo = timezone(self._tz_name_for_route_day(person=person, route=route))
        return utc.localize(start).astimezone(tzinfo).date()

    def _scheduled_start_on_dayroute_date(self, current_start, dayroute, person=None):
        """Move a UTC-naive start onto the dayroute date in the worker timezone."""
        person = person or dayroute.person_id
        tzinfo = timezone(
            self._tz_name_for_route_day(person=person, route=dayroute.route_id)
        )
        if current_start:
            local = utc.localize(fields.Datetime.to_datetime(current_start)).astimezone(
                tzinfo
            )
            # Re-localize on the target date so DST offset is recalculated.
            naive_local = local.replace(tzinfo=None).replace(
                year=dayroute.date.year,
                month=dayroute.date.month,
                day=dayroute.date.day,
            )
            return tzinfo.localize(naive_local).astimezone(utc).replace(tzinfo=None)
        if dayroute.date_start_planned:
            return dayroute.date_start_planned
        local = tzinfo.localize(datetime.combine(dayroute.date, time(8, 0)))
        return local.astimezone(utc).replace(tzinfo=None)

    def _capture_duration_from_start_end(self, write_vals):
        """Store duration from supplied start/end before the start date is moved."""
        if "scheduled_duration" in write_vals:
            return write_vals
        start = write_vals.get("scheduled_date_start")
        end = write_vals.get("scheduled_date_end")
        if not (start and end):
            return write_vals
        start_dt = fields.Datetime.to_datetime(start)
        end_dt = fields.Datetime.to_datetime(end)
        write_vals["scheduled_duration"] = (end_dt - start_dt).total_seconds() / 3600
        return write_vals

    def _duration_for_schedule_sync(self, write_vals):
        if "scheduled_duration" in write_vals:
            return write_vals.get("scheduled_duration") or 0.0
        start = write_vals.get("scheduled_date_start")
        end = write_vals.get("scheduled_date_end")
        if start and end:
            start_dt = fields.Datetime.to_datetime(start)
            end_dt = fields.Datetime.to_datetime(end)
            return (end_dt - start_dt).total_seconds() / 3600
        return self.scheduled_duration or 0.0

    def _sync_scheduled_end_from_start(self, write_vals):
        """Keep end/duration aligned after scheduled_date_start is established."""
        start = write_vals.get("scheduled_date_start")
        if not start:
            return write_vals
        start = fields.Datetime.to_datetime(start)
        duration = self._duration_for_schedule_sync(write_vals)
        write_vals["scheduled_duration"] = duration
        write_vals["scheduled_date_end"] = start + timedelta(hours=duration)
        return write_vals

    def _get_dayroute_values(self, vals):
        route_id = self._get_route_id_from_vals(vals)
        person_id = self._get_person_id_for_dayroute(vals, route_id)
        person = (
            self.env["fsm.person"].browse(person_id) if person_id else self.person_id
        )
        route = (
            self.env["fsm.route"].browse(route_id) if route_id else self.fsm_route_id
        )
        scheduled_start = vals.get("scheduled_date_start") or self.scheduled_date_start
        date = self._local_date_from_scheduled_start(
            scheduled_start, person=person, route=route
        )
        return {
            "person_id": person_id,
            "date": date,
            "route_id": route_id,
            "team_id": self._get_team_id_for_dayroute(vals),
        }

    def _get_dayroute_domain(self, values):
        return [
            ("person_id", "=", values["person_id"]),
            ("date", "=", values["date"]),
            ("route_id", "=", values.get("route_id") or False),
            ("team_id", "=", values.get("team_id") or False),
            ("order_remaining", ">", 0),
        ]

    def _dayroute_matches_values(self, dayroute, values):
        return bool(
            dayroute
            and dayroute.person_id.id == values["person_id"]
            and dayroute.date == values["date"]
            and (dayroute.route_id.id or False) == (values.get("route_id") or False)
            and (dayroute.team_id.id or False) == (values.get("team_id") or False)
        )

    def _can_create_dayroute(self, values):
        return values["person_id"] and values["date"]

    def _unlink_empty_dayroutes(self, dayroutes):
        # Automatic cleanup must work for FSM users who can reschedule but
        # do not have unlink rights on day routes.
        empty = dayroutes.filtered(lambda dayroute: dayroute and not dayroute.order_ids)
        empty.sudo().unlink()

    def _manage_fsm_route(self, vals):
        dayroute_obj = self.env["fsm.route.dayroute"]
        values = self._get_dayroute_values(vals)
        # Keep the current day route when it still matches: the order already
        # occupies a slot, so order_remaining may be 0 on a full route.
        if self._dayroute_matches_values(self.dayroute_id, values):
            vals.update({"dayroute_id": self.dayroute_id.id})
            return vals
        domain = self._get_dayroute_domain(values)
        dayroute = dayroute_obj.search(domain, limit=1)
        if dayroute:
            vals.update({"dayroute_id": dayroute.id})
        elif self._can_create_dayroute(values):
            dayroute = dayroute_obj.create(self.prepare_dayroute_values(values))
            vals.update({"dayroute_id": dayroute.id})
        else:
            # e.g. moved to an unstaffed route: drop the stale day route.
            vals.update({"dayroute_id": False})
            if not values["person_id"] and self._route_id_changing(
                vals, values.get("route_id")
            ):
                vals["person_id"] = False
        return vals

    def _reassign_dayroute_for_person_timezone(self):
        """Re-evaluate dayroute after the worker/timezone or route changes."""
        self.ensure_one()
        if not self.scheduled_date_start:
            return
        if not self.person_id:
            if self.dayroute_id:
                self.write({"dayroute_id": False})
            return
        old_dayroute = self.dayroute_id
        managed = self._manage_fsm_route(
            {
                "person_id": self.person_id.id,
                "scheduled_date_start": self.scheduled_date_start,
            }
        )
        new_dayroute_id = managed.get("dayroute_id")
        if new_dayroute_id and new_dayroute_id != old_dayroute.id:
            self.write({"dayroute_id": new_dayroute_id})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("fsm_route_id") and vals.get("location_id"):
                location = self.env["fsm.location"].browse(vals["location_id"])
                vals.update({"fsm_route_id": location.fsm_route_id.id})

            if vals.get("dayroute_id"):
                order = self.new(vals)
                dayroute = self.env["fsm.route.dayroute"].browse(vals["dayroute_id"])
                vals.update(order._prepare_vals_from_dayroute(dayroute, vals))
            elif vals.get("person_id") and vals.get("scheduled_date_start"):
                vals = self._manage_fsm_route(vals)
        return super().create(vals_list)

    def _prepare_route_write_vals(self, vals):
        write_vals = dict(vals)
        if {
            "scheduled_date_end",
            "scheduled_duration",
            "scheduled_date_start",
        } & write_vals.keys():
            self._calc_scheduled_dates(write_vals)
            # Include start when only end was derived so super().write()'s
            # second _calc_scheduled_dates takes the start+end branch.
            # Otherwise duration 0 is falsy and the end-only branch recomputes
            # start from the still-unwritten previous duration.
            if (
                write_vals.get("scheduled_date_end")
                and "scheduled_date_start" not in write_vals
                and self.scheduled_date_start
            ):
                write_vals["scheduled_date_start"] = self.scheduled_date_start
        return write_vals

    def _is_unscheduling(self, vals):
        return "scheduled_date_start" in vals and not vals.get("scheduled_date_start")

    def _order_route_for_dayroute_write(self, write_vals):
        location_id = write_vals.get("location_id") or self.location_id.id
        if location_id:
            return self.env["fsm.location"].browse(location_id).fsm_route_id
        return self.fsm_route_id

    def _prepare_vals_from_dayroute(self, dayroute, write_vals):
        """Make an explicit day route authoritative for person and schedule date."""
        write_vals = dict(write_vals)
        if not dayroute:
            return write_vals
        order_route = self._order_route_for_dayroute_write(write_vals)
        dayroute_route_id = dayroute.route_id.id if dayroute.route_id else False
        order_route_id = order_route.id if order_route else False
        if dayroute_route_id != order_route_id:
            raise ValidationError(
                self.env._(
                    "The day route %(dayroute)s belongs to route %(route)s, "
                    "which does not match the order route %(order_route)s.",
                    dayroute=dayroute.display_name,
                    route=dayroute.route_id.display_name
                    if dayroute.route_id
                    else self.env._("no route"),
                    order_route=order_route.display_name
                    if order_route
                    else self.env._("no route"),
                )
            )
        if dayroute.person_id:
            write_vals["person_id"] = dayroute.person_id.id
        # Day route owns the calendar via team; keep the order aligned.
        if dayroute.team_id:
            write_vals["team_id"] = dayroute.team_id.id
        if dayroute.date:
            write_vals = self._capture_duration_from_start_end(write_vals)
            current_start = (
                write_vals.get("scheduled_date_start") or self.scheduled_date_start
            )
            write_vals["scheduled_date_start"] = self._scheduled_start_on_dayroute_date(
                current_start,
                dayroute,
                person=dayroute.person_id,
            )
            write_vals = self._sync_scheduled_end_from_start(write_vals)
        return write_vals

    def _write_with_route_management(self, vals):
        self.ensure_one()
        write_vals = self._prepare_route_write_vals(vals)
        dayroutes_to_check = self.env["fsm.route.dayroute"]

        if self._is_unscheduling(write_vals):
            dayroutes_to_check |= self.dayroute_id
            write_vals["dayroute_id"] = False
            res = super().write(write_vals)
            self._unlink_empty_dayroutes(dayroutes_to_check)
            return res

        if "person_id" in write_vals and not write_vals.get("person_id"):
            dayroutes_to_check |= self.dayroute_id
            write_vals["dayroute_id"] = False
            res = super().write(write_vals)
            self._unlink_empty_dayroutes(dayroutes_to_check)
            return res

        if "dayroute_id" in write_vals:
            dayroutes_to_check |= self.dayroute_id
            new_dayroute = self.env["fsm.route.dayroute"].browse(
                write_vals.get("dayroute_id") or []
            )
            write_vals = self._prepare_vals_from_dayroute(new_dayroute, write_vals)
            res = super().write(write_vals)
            self._unlink_empty_dayroutes(dayroutes_to_check)
            return res

        if (write_vals.get("person_id") or self.person_id) and (
            write_vals.get("scheduled_date_start") or self.scheduled_date_start
        ):
            dayroutes_to_check |= self.dayroute_id
            write_vals = self._manage_fsm_route(write_vals)

        res = super().write(write_vals)
        self._unlink_empty_dayroutes(dayroutes_to_check)
        return res

    def write(self, vals):
        route_trigger_fields = self._ROUTE_WRITE_FIELDS | {
            "scheduled_date_end",
            "scheduled_duration",
        }
        if not route_trigger_fields.intersection(vals):
            return super().write(vals)
        if len(self) == 1:
            return self._write_with_route_management(vals)
        for order in self:
            order._write_with_route_management(vals)
        return True
