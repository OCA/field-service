# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta
from unittest.mock import patch

from pytz import timezone, utc

from odoo.exceptions import AccessError, ValidationError
from odoo.tools import mute_logger

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMRouteDayRoute(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.DayRoute = cls.env["fsm.route.dayroute"]
        cls.Route = cls.env["fsm.route"]
        cls.monday = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.route = cls.Route.create(
            {
                "name": "Worker Route",
                "max_order": 5,
                "fsm_person_id": cls.test_person.id,
                "day_ids": [(6, 0, [cls.monday.id])],
            }
        )

    def _next_weekday(self, weekday):
        date = datetime.now().date()
        while date.weekday() != weekday:
            date += timedelta(days=1)
        return date

    def test_default_team_required(self):
        with mute_logger("odoo.models.unlink"):
            self.env["fsm.team"].search([]).unlink()
        with self.assertRaisesRegex(
            ValidationError, "You must create a FSM team first."
        ):
            self.DayRoute.create(
                {
                    "route_id": self.route.id,
                    "date": self._next_weekday(0),
                }
            )

    def test_person_without_route_worker(self):
        route = self.Route.create(
            {
                "name": "Unstaffed Route",
                "day_ids": [(6, 0, [self.monday.id])],
            }
        )
        dayroute = self.DayRoute.create(
            {
                "route_id": route.id,
                "date": self._next_weekday(0),
            }
        )
        self.assertFalse(dayroute.person_id)

    def test_compute_date_start_planned_without_date(self):
        dayroute = self.DayRoute.new({"route_id": self.route.id})
        dayroute._compute_date_start_planned()
        self.assertFalse(dayroute.date_start_planned)

    def test_create_without_route_id_with_person(self):
        route_date = self._next_weekday(0)
        dayroute = self.DayRoute.create(
            {
                "date": route_date,
                "person_id": self.test_person.id,
            }
        )
        self.assertTrue(dayroute.date_start_planned)

    def test_planned_start_uses_route_worker(self):
        route_date = self._next_weekday(0)
        planned = self.DayRoute._planned_start_from_date(
            route_date,
            route=self.route,
        )
        self.assertTrue(planned)

    def test_planned_start_company_calendar_timezone(self):
        route_date = self._next_weekday(0)
        self.test_person.partner_id.tz = False
        self.test_person.calendar_id = False
        self.env.company.resource_calendar_id.tz = "UTC"
        planned = self.DayRoute._planned_start_from_date(
            route_date,
            person=self.test_person,
            route=self.route,
        )
        self.assertTrue(planned)

    def test_planned_start_user_timezone_fallback(self):
        route_date = self._next_weekday(0)
        self.test_person.partner_id.tz = False
        self.test_person.calendar_id = False
        calendar = self.env.company.resource_calendar_id
        with (
            patch.object(type(calendar), "_get_closest_work_time", return_value=None),
            patch.object(type(calendar), "tz", False),
            patch.object(type(self.env.user), "tz", False),
        ):
            planned = self.DayRoute._planned_start_from_date(
                route_date,
                person=self.test_person,
                route=self.route,
            )
        self.assertTrue(planned)

    def test_check_day_skipped_without_route_or_date(self):
        dayroute = self.DayRoute.new({})
        dayroute.check_day()

    def test_create_without_route_id(self):
        route_date = self._next_weekday(0)
        dayroute = self.DayRoute.create({"date": route_date})
        self.assertTrue(dayroute.date_start_planned)

    def test_compute_date_start_clears_without_date(self):
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": self._next_weekday(0),
            }
        )
        dayroute.write({"date": False})
        self.assertFalse(dayroute.date_start_planned)

    def test_planned_start_without_work_interval(self):
        route_date = self._next_weekday(0)
        calendar = self.env["resource.calendar"].create(
            {
                "name": "No Attendance",
                "tz": "UTC",
                "attendance_ids": [],
            }
        )
        self.test_person.calendar_id = calendar
        with patch.object(type(calendar), "_get_closest_work_time", return_value=None):
            planned = self.DayRoute._planned_start_from_date(
                route_date,
                person=self.test_person,
                route=self.route,
            )
        self.assertTrue(planned)

    def test_dayroute_create_with_date_start_planned(self):
        route_date = self._next_weekday(0)
        planned = self.DayRoute._planned_start_from_date(
            route_date,
            route=self.route,
        )
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
                "date_start_planned": planned,
            }
        )
        self.assertEqual(dayroute.date_start_planned, planned)

    def test_compute_date_start_uses_dayroute_person(self):
        other_person = self.env["fsm.person"].create({"name": "Other Worker"})
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": self._next_weekday(0),
                "person_id": other_person.id,
            }
        )
        dayroute.invalidate_recordset(["date_start_planned"])
        dayroute._compute_date_start_planned()
        self.assertTrue(dayroute.date_start_planned)

    def test_portal_user_sees_only_own_dayroutes(self):
        other_person = self.env["fsm.person"].create({"name": "Other Worker"})
        route_date = self._next_weekday(0)
        own_dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        other_route = self.Route.create(
            {
                "name": "Other Worker Route",
                "max_order": 5,
                "fsm_person_id": other_person.id,
                "day_ids": [(6, 0, [self.monday.id])],
            }
        )
        other_dayroute = self.DayRoute.create(
            {
                "route_id": other_route.id,
                "date": route_date,
            }
        )
        portal_user = self.env["res.users"].create(
            {
                "name": self.test_person.name,
                "login": "portal_route_worker",
                "partner_id": self.test_person.partner_id.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        portal_dayroutes = self.DayRoute.with_user(portal_user).search([])
        self.assertIn(own_dayroute, portal_dayroutes)
        self.assertNotIn(other_dayroute, portal_dayroutes)

    def test_portal_user_cannot_write_dayroutes(self):
        route_date = self._next_weekday(0)
        own_dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        portal_user = self.env["res.users"].create(
            {
                "name": self.test_person.name,
                "login": "portal_route_worker_write",
                "partner_id": self.test_person.partner_id.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        with self.assertRaises(AccessError):
            own_dayroute.with_user(portal_user).write({"name": "Portal edit"})

    def test_planned_start_recomputes_on_two_week_calendar(self):
        route_date = self._next_weekday(0)
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Two Week Shift",
                "tz": "UTC",
                "two_weeks_calendar": True,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Week 1 Monday",
                            "dayofweek": "0",
                            "week_type": "0",
                            "hour_from": 7.0,
                            "hour_to": 15.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        self.test_person.calendar_id = calendar
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        before = dayroute.date_start_planned
        calendar.attendance_ids.write({"week_type": "1"})
        self.assertNotEqual(dayroute.date_start_planned, before)

    def test_planned_start_uses_team_company_calendar(self):
        route_date = self._next_weekday(0)
        other_company = self.env["res.company"].create({"name": "Other Company"})
        other_calendar = self.env["resource.calendar"].create(
            {
                "name": "Other Company Calendar",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Other Shift",
                            "dayofweek": str(route_date.weekday()),
                            "hour_from": 5.0,
                            "hour_to": 13.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        other_company.resource_calendar_id = other_calendar
        other_team = self.env["fsm.team"].create(
            {
                "name": "Other Company Team",
                "company_id": other_company.id,
            }
        )
        self.test_person.calendar_id = False
        dayroute = self.DayRoute.with_company(other_company).create(
            {
                "route_id": self.route.id,
                "date": route_date,
                "team_id": other_team.id,
            }
        )
        planned = dayroute.date_start_planned
        self.assertTrue(planned)
        self.assertEqual(planned.hour, 5)

    def test_create_sequence_fallback(self):
        route_date = self._next_weekday(0)
        with patch.object(
            type(self.env["ir.sequence"]),
            "next_by_code",
            return_value=False,
        ):
            dayroute = self.DayRoute.create(
                {
                    "route_id": self.route.id,
                    "date": route_date,
                }
            )
        self.assertEqual(dayroute.name, "New")

    def test_order_remaining_recomputes_on_max_order_change(self):
        route_date = self._next_weekday(0)
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        self.assertEqual(dayroute.order_remaining, 5)
        self.route.max_order = 3
        self.assertEqual(dayroute.order_remaining, 3)

    def test_default_team_uses_active_company(self):
        other_company = self.env["res.company"].create({"name": "Active Company"})
        self.env["fsm.team"].search(
            [("company_id", "in", (self.env.company.id, False))]
        ).write({"sequence": 100})
        other_team = self.env["fsm.team"].create(
            {
                "name": "Active Company Team",
                "company_id": other_company.id,
                "sequence": 1,
            }
        )
        dayroute = self.DayRoute.with_company(other_company).create(
            {
                "route_id": self.route.id,
                "date": self._next_weekday(0),
            }
        )
        self.assertEqual(dayroute.team_id, other_team)

    def test_create_without_team_uses_default_team_calendar(self):
        route_date = self._next_weekday(0)
        other_company = self.env["res.company"].create({"name": "Default Team Co"})
        other_calendar = self.env["resource.calendar"].create(
            {
                "name": "Default Team Calendar",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Early",
                            "dayofweek": str(route_date.weekday()),
                            "hour_from": 4.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        other_company.resource_calendar_id = other_calendar
        self.env["fsm.team"].search(
            [("company_id", "in", (self.env.company.id, False))]
        ).write({"sequence": 100})
        other_team = self.env["fsm.team"].create(
            {
                "name": "Default Team Calendar Team",
                "company_id": other_company.id,
                "sequence": 1,
            }
        )
        self.test_person.calendar_id = False
        dayroute = self.DayRoute.with_company(other_company).create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        self.assertEqual(dayroute.team_id, other_team)
        self.assertEqual(dayroute.date_start_planned.hour, 4)

    def test_portal_user_cannot_read_ir_sequence(self):
        portal_user = self.env["res.users"].create(
            {
                "name": self.test_person.name,
                "login": "portal_route_sequence",
                "partner_id": self.test_person.partner_id.id,
                "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        sequence = self.env.ref("fieldservice_route.seq_fsm_route")
        with self.assertRaises(AccessError):
            sequence.with_user(portal_user).read(["name"])

    def test_create_with_custom_name_skips_sequence(self):
        route_date = self._next_weekday(0)
        dayroute = self.DayRoute.create(
            {
                "name": "Custom Day Route",
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        self.assertEqual(dayroute.name, "Custom Day Route")

    def test_create_with_explicit_team_id(self):
        route_date = self._next_weekday(0)
        team = self.env["fsm.team"].search([], limit=1)
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
                "team_id": team.id,
            }
        )
        self.assertEqual(dayroute.team_id, team)
        self.assertTrue(dayroute.date_start_planned)

    def test_default_stage_id(self):
        stage = self.DayRoute._default_stage_id()
        self.assertTrue(stage)
        self.assertEqual(stage.stage_type, "route")

    def test_planned_start_without_calendar(self):
        route_date = self._next_weekday(0)
        other_company = self.env["res.company"].create({"name": "No Calendar Co"})
        other_company.resource_calendar_id = False
        other_team = self.env["fsm.team"].create(
            {
                "name": "No Calendar Team",
                "company_id": other_company.id,
            }
        )
        person = self.env["fsm.person"].create({"name": "No Calendar Worker"})
        person.calendar_id = False
        person.partner_id.tz = "UTC"
        planned = self.DayRoute._planned_start_from_date(
            route_date,
            person=person,
            team=other_team,
        )
        self.assertEqual(planned.hour, 8)

    def test_check_capacity_allows_equal_max_order(self):
        route = self.Route.create(
            {
                "name": "Exact Capacity",
                "max_order": 1,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, [self.monday.id])],
            }
        )
        location = self.env["fsm.location"].create(
            {
                "name": "Exact Capacity Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        dayroute = self.DayRoute.create(
            {
                "route_id": route.id,
                "date": self._next_weekday(0),
            }
        )
        self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "dayroute_id": dayroute.id,
            }
        )
        dayroute.invalidate_recordset()
        self.assertEqual(dayroute.order_count, 1)
        dayroute.check_capacity()

    def _assert_planned_start_search_range_uses_local_midnights(
        self, route_date, tz_name
    ):
        tzinfo = timezone(tz_name)
        expected_start = tzinfo.localize(datetime.combine(route_date, time.min))
        expected_end = tzinfo.localize(
            datetime.combine(route_date + timedelta(days=1), time.min)
        )
        calendar = self.env["resource.calendar"].create(
            {
                "name": f"DST {tz_name} {route_date}",
                "tz": tz_name,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Shift",
                            "dayofweek": str(route_date.weekday()),
                            "hour_from": 9.0,
                            "hour_to": 17.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        self.test_person.partner_id.tz = tz_name
        self.test_person.calendar_id = calendar
        captured = {}

        work_time = tzinfo.localize(datetime.combine(route_date, time(9, 0)))

        def _capture_closest_work_time(
            _self, start, match_end=False, search_range=None, compute_leaves=True
        ):
            captured["search_range"] = search_range
            return work_time

        with patch.object(
            type(calendar),
            "_get_closest_work_time",
            autospec=True,
            side_effect=_capture_closest_work_time,
        ):
            planned = self.DayRoute._planned_start_from_date(
                route_date,
                person=self.test_person,
                route=self.route,
            )
        self.assertEqual(captured["search_range"], (expected_start, expected_end))
        self.assertEqual(planned, work_time.astimezone(utc).replace(tzinfo=None))

    def test_planned_start_search_range_spring_forward_dst(self):
        # US/Eastern spring forward 2026-03-08 (EST -> EDT).
        self._assert_planned_start_search_range_uses_local_midnights(
            datetime(2026, 3, 8).date(), "US/Eastern"
        )

    def test_planned_start_search_range_fall_back_dst(self):
        # US/Eastern fall back 2026-11-01 (EDT -> EST).
        self._assert_planned_start_search_range_uses_local_midnights(
            datetime(2026, 11, 1).date(), "US/Eastern"
        )
