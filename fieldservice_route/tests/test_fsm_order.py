# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from pytz import timezone, utc

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMOrderRoute(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.fsm_route_obj = cls.env["fsm.route"]
        date = datetime.now()
        cls.date = date.replace(microsecond=0)
        cls.days = [
            cls.env.ref("fieldservice_route.fsm_route_day_0").id,
            cls.env.ref("fieldservice_route.fsm_route_day_1").id,
            cls.env.ref("fieldservice_route.fsm_route_day_2").id,
            cls.env.ref("fieldservice_route.fsm_route_day_3").id,
            cls.env.ref("fieldservice_route.fsm_route_day_4").id,
            cls.env.ref("fieldservice_route.fsm_route_day_5").id,
            cls.env.ref("fieldservice_route.fsm_route_day_6").id,
        ]
        cls.fsm_route_id = cls.fsm_route_obj.create(
            {
                "name": "Demo Route",
                "max_order": 10,
                "fsm_person_id": cls.test_person.id,
                "day_ids": [(6, 0, cls.days)],
            }
        )
        cls.test_location.fsm_route_id = cls.fsm_route_id.id

    def test_create_day_route(self):
        order_form = Form(self.env["fsm.order"])
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = self.date
        order = order_form.save()
        self.assertEqual(order.person_id, self.test_person)
        self.assertEqual(order.fsm_route_id, self.test_location.fsm_route_id)
        self.assertEqual(order.dayroute_id.person_id, order.person_id)
        self.assertEqual(order.dayroute_id.date, order.scheduled_date_start.date())
        self.assertEqual(order.dayroute_id.route_id, order.fsm_route_id)

    def test_date_start_planned_uses_worker_schedule(self):
        route_date = self.date.date()
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Early Shift",
                "tz": "US/Eastern",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Shift",
                            "dayofweek": str(route_date.weekday()),
                            "hour_from": 6.0,
                            "hour_to": 14.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        self.test_person.partner_id.tz = "US/Eastern"
        self.test_person.calendar_id = calendar
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": route_date,
            }
        )
        actual_local = utc.localize(dayroute.date_start_planned).astimezone(
            timezone("US/Eastern")
        )
        self.assertEqual(actual_local.hour, 6)
        self.assertEqual(actual_local.minute, 0)

    def test_date_start_planned_recomputes_on_calendar_change(self):
        route_date = self.date.date()
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Morning Shift",
                "tz": "US/Eastern",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Shift",
                            "dayofweek": str(route_date.weekday()),
                            "hour_from": 7.0,
                            "hour_to": 15.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        self.test_person.partner_id.tz = "US/Eastern"
        self.test_person.calendar_id = calendar
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": route_date,
            }
        )
        before = utc.localize(dayroute.date_start_planned).astimezone(
            timezone("US/Eastern")
        )
        self.assertEqual(before.hour, 7)
        calendar.attendance_ids.write({"hour_from": 9.0})
        after = utc.localize(dayroute.date_start_planned).astimezone(
            timezone("US/Eastern")
        )
        self.assertEqual(after.hour, 9)

    def test_date_start_planned_fallback_without_calendar(self):
        route_date = self.date.date()
        empty_calendar = self.env["resource.calendar"].create(
            {
                "name": "Empty Schedule",
                "tz": "US/Eastern",
                "attendance_ids": [],
            }
        )
        self.test_person.calendar_id = empty_calendar
        self.test_person.partner_id.tz = "US/Eastern"
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": route_date,
            }
        )
        actual_local = utc.localize(dayroute.date_start_planned).astimezone(
            timezone("US/Eastern")
        )
        self.assertEqual(actual_local.hour, 8)
        self.assertEqual(actual_local.minute, 0)

    def test_reuse_existing_dayroute(self):
        order1 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order1.dayroute_id, order2.dayroute_id)
        self.assertEqual(order1.dayroute_id.order_count, 2)

    def test_order_person_from_route(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
            }
        )
        self.assertEqual(order.person_id, self.fsm_route_id.fsm_person_id)

    def test_order_sets_route_from_location(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
            }
        )
        self.assertEqual(order.fsm_route_id, self.test_location.fsm_route_id)

    def test_order_write_scheduled_date_start(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        dayroute = order.dayroute_id
        new_date = self.date + timedelta(days=1)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        order.write({"scheduled_date_start": new_date})
        self.assertNotEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.dayroute_id.date, new_date.date())

    def test_get_dayroute_values_string_datetime(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        values = order._get_dayroute_values(
            {
                "scheduled_date_start": self.date.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                ),
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(values["date"], self.date.date())
        self.assertEqual(values["person_id"], self.test_person.id)

    def test_prepare_dayroute_values_and_domain(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        team = order._get_team_id_for_dayroute({})
        values = {
            "person_id": self.test_person.id,
            "date": self.date.date(),
            "route_id": self.fsm_route_id.id,
            "team_id": team,
        }
        prepared = order.prepare_dayroute_values(values)
        self.assertEqual(prepared, values)
        domain = order._get_dayroute_domain(values)
        self.assertEqual(
            domain,
            [
                ("person_id", "=", self.test_person.id),
                ("date", "=", self.date.date()),
                ("route_id", "=", self.fsm_route_id.id),
                ("team_id", "=", team),
                ("order_remaining", ">", 0),
            ],
        )
        routeless_domain = order._get_dayroute_domain(
            {
                "person_id": self.test_person.id,
                "date": self.date.date(),
                "route_id": False,
                "team_id": team,
            }
        )
        self.assertEqual(
            routeless_domain,
            [
                ("person_id", "=", self.test_person.id),
                ("date", "=", self.date.date()),
                ("route_id", "=", False),
                ("team_id", "=", team),
                ("order_remaining", ">", 0),
            ],
        )
        self.assertTrue(order._can_create_dayroute(values))
        self.assertFalse(
            order._can_create_dayroute({"person_id": False, "date": False})
        )

    def test_manage_fsm_route_skips_create_without_worker(self):
        route = self.fsm_route_obj.create(
            {
                "name": "Route Without Worker",
                "max_order": 5,
                "day_ids": [(6, 0, self.days)],
            }
        )
        location = self.env["fsm.location"].create(
            {
                "name": "Route Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        order = self.env["fsm.order"].new({"location_id": location.id})
        vals = order._manage_fsm_route({"scheduled_date_start": self.date})
        self.assertFalse(vals.get("dayroute_id"))

    def test_manage_fsm_route_unlinks_empty_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        new_date = self.date + timedelta(days=7)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        order.write({"scheduled_date_start": new_date})
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_two_routes_same_worker_same_date(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Second Demo Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Second Route Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": other_route.id,
            }
        )
        order1 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": other_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertNotEqual(order1.dayroute_id, order2.dayroute_id)
        self.assertEqual(order1.dayroute_id.route_id, self.fsm_route_id)
        self.assertEqual(order2.dayroute_id.route_id, other_route)

    def test_get_dayroute_values_from_record_scheduled_date(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
            }
        )
        values = order._get_dayroute_values({})
        self.assertEqual(values["date"], self.date.date())
        self.assertEqual(values["route_id"], self.fsm_route_id.id)

    def test_get_dayroute_values_datetime_object(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        values = order._get_dayroute_values(
            {
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
                "fsm_route_id": self.fsm_route_id.id,
            }
        )
        self.assertEqual(values["date"], self.date.date())

    def test_create_without_dayroute_assignment(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        self.assertFalse(order.dayroute_id)

    def test_create_only_scheduled_without_person(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
            }
        )
        self.assertFalse(order.dayroute_id)

    def test_write_skips_route_management(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        dayroute = order.dayroute_id
        order.write({"description": "No route update"})
        self.assertEqual(order.dayroute_id, dayroute)

    def test_bulk_write_description_keeps_dayroutes(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Bulk Write Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Bulk Write Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": other_route.id,
            }
        )
        order1 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": other_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        dayroute1 = order1.dayroute_id
        dayroute2 = order2.dayroute_id
        (order1 + order2).write({"description": "Bulk update"})
        self.assertEqual(order1.dayroute_id, dayroute1)
        self.assertEqual(order2.dayroute_id, dayroute2)
        self.assertNotEqual(dayroute1, dayroute2)

    def test_write_clear_scheduled_date_clears_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        order.write({"scheduled_date_start": False})
        self.assertFalse(order.scheduled_date_start)
        self.assertFalse(order.dayroute_id)
        self.assertFalse(old_dayroute.exists())

    def test_write_location_change_updates_dayroute(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Location Change Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Location Change Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": other_route.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        order.write({"location_id": other_location.id})
        self.assertEqual(order.fsm_route_id, other_route)
        self.assertEqual(order.dayroute_id.route_id, other_route)
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_routeless_order_does_not_reuse_routed_dayroute(self):
        routeless_location = self.env["fsm.location"].create(
            {
                "name": "Routeless Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        routed_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": routeless_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertNotEqual(order.dayroute_id, routed_dayroute)
        self.assertFalse(order.dayroute_id.route_id)

    def test_write_scheduled_date_end_updates_dayroute(self):
        monday = self.date
        while monday.weekday() != 0:
            monday -= timedelta(days=1)
        tuesday = monday + timedelta(days=1)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": monday.replace(hour=22, minute=0),
                "scheduled_duration": 4.0,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.dayroute_id.date, monday.date())
        order.write(
            {
                "scheduled_date_end": tuesday.replace(hour=18, minute=0),
            }
        )
        self.assertEqual(order.scheduled_date_start.date(), tuesday.date())
        self.assertEqual(order.dayroute_id.date, tuesday.date())

    def test_write_direct_dayroute_id_clears_old_dayroute(self):
        self.test_person.partner_id.tz = "UTC"
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        original_local = utc.localize(order.scheduled_date_start).astimezone(
            timezone("UTC")
        )
        new_date = self.date + timedelta(days=7)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        new_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": new_date.date(),
            }
        )
        order.write({"dayroute_id": new_dayroute.id})
        self.assertEqual(order.dayroute_id, new_dayroute)
        local_after = utc.localize(order.scheduled_date_start).astimezone(
            timezone("UTC")
        )
        self.assertEqual(local_after.date(), new_dayroute.date)
        self.assertEqual(local_after.time(), original_local.time())
        self.assertEqual(order.person_id, new_dayroute.person_id)
        self.assertFalse(old_dayroute.exists())

    def test_write_direct_dayroute_rejects_route_mismatch(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Mismatch Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        other_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": other_route.id,
                "date": self.date.date(),
            }
        )
        with self.assertRaises(ValidationError):
            order.write({"dayroute_id": other_dayroute.id})

    def test_write_zero_duration_keeps_dayroute_date(self):
        tuesday = self.date
        while tuesday.weekday() != 1:
            tuesday += timedelta(days=1)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": tuesday.replace(hour=0, minute=30),
                "scheduled_duration": 2.0,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.dayroute_id.date, tuesday.date())
        order.write({"scheduled_duration": 0.0})
        self.assertEqual(order.scheduled_date_start.date(), tuesday.date())
        self.assertEqual(order.dayroute_id.date, tuesday.date())
        self.assertEqual(order.scheduled_duration, 0.0)

    def test_write_direct_dayroute_removal_clears_old_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        order.write({"dayroute_id": False})
        self.assertFalse(order.dayroute_id)
        self.assertFalse(old_dayroute.exists())

    def test_order_create_multi(self):
        # Use midday so +1h cannot cross a local/UTC midnight day boundary.
        self.test_person.partner_id.tz = "UTC"
        start = self.date.replace(hour=12, minute=0, second=0, microsecond=0)
        orders = self.env["fsm.order"].create(
            [
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": start,
                    "person_id": self.test_person.id,
                },
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": start + timedelta(hours=1),
                    "person_id": self.test_person.id,
                },
            ]
        )
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].dayroute_id, orders[1].dayroute_id)
        self.assertEqual(orders[0].dayroute_id.date, start.date())

    def test_get_route_id_from_vals_prefers_fsm_route_id(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Explicit Route",
                "max_order": 5,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        self.assertEqual(
            order._get_route_id_from_vals({"fsm_route_id": other_route.id}),
            other_route.id,
        )

    def test_get_route_id_from_vals_without_location(self):
        order = self.env["fsm.order"].new({})
        self.assertFalse(order._get_route_id_from_vals({}))

    def test_get_person_id_for_dayroute_from_route(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        person_id = order._get_person_id_for_dayroute({}, self.fsm_route_id.id)
        self.assertEqual(person_id, self.test_person.id)

    def test_get_person_id_for_dayroute_from_order_person(self):
        other_person = self.env["fsm.person"].create({"name": "Fallback Worker"})
        order = self.env["fsm.order"].new(
            {
                "location_id": self.test_location.id,
                "person_id": other_person.id,
            }
        )
        person_id = order._get_person_id_for_dayroute({}, False)
        self.assertEqual(person_id, other_person.id)

    def test_write_person_id_reassigns_dayroute(self):
        other_person = self.env["fsm.person"].create({"name": "Other Assignee"})
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        order.write({"person_id": other_person.id})
        self.assertEqual(order.dayroute_id.person_id, other_person)
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_bulk_write_scheduled_date_keeps_separate_dayroutes(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Bulk Schedule Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Bulk Schedule Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": other_route.id,
            }
        )
        order1 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": other_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        new_date = self.date + timedelta(days=1)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        (order1 + order2).write({"scheduled_date_start": new_date})
        self.assertEqual(order1.dayroute_id.date, new_date.date())
        self.assertEqual(order2.dayroute_id.date, new_date.date())
        self.assertNotEqual(order1.dayroute_id, order2.dayroute_id)
        self.assertEqual(order1.dayroute_id.route_id, self.fsm_route_id)
        self.assertEqual(order2.dayroute_id.route_id, other_route)

    def test_write_direct_dayroute_uses_planned_start_when_unscheduled(self):
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        self.assertFalse(order.scheduled_date_start)
        order.write({"dayroute_id": dayroute.id})
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.scheduled_date_start, dayroute.date_start_planned)
        self.assertEqual(order.person_id, dayroute.person_id)

    def test_write_direct_dayroute_uses_date_when_no_planned_start(self):
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        dayroute.write({"date_start_planned": False})
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        order.write({"dayroute_id": dayroute.id})
        self.assertEqual(order.scheduled_date_start.date(), dayroute.date)

    def test_order_route_for_dayroute_write_without_location(self):
        order = self.env["fsm.order"].new({})
        self.assertFalse(order._order_route_for_dayroute_write({}))

    def test_prepare_vals_from_dayroute_empty(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        vals = order._prepare_vals_from_dayroute(
            self.env["fsm.route.dayroute"], {"dayroute_id": False}
        )
        self.assertEqual(vals, {"dayroute_id": False})

    def test_create_with_full_dayroute_creates_another(self):
        route = self.fsm_route_obj.create(
            {
                "name": "Capacity One",
                "max_order": 1,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        location = self.env["fsm.location"].create(
            {
                "name": "Capacity Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        order1 = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertNotEqual(order1.dayroute_id, order2.dayroute_id)
        self.assertEqual(order1.dayroute_id.order_count, 1)
        self.assertEqual(order2.dayroute_id.order_count, 1)

    def test_write_location_and_dayroute_together(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Combined Write Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Combined Write Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": other_route.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        new_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": other_route.id,
                "date": self.date.date(),
            }
        )
        order.write(
            {
                "location_id": other_location.id,
                "dayroute_id": new_dayroute.id,
            }
        )
        self.assertEqual(order.location_id, other_location)
        self.assertEqual(order.dayroute_id, new_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_unlink_empty_dayroutes_ignores_empty_recordset(self):
        order = self.env["fsm.order"].new({})
        order._unlink_empty_dayroutes(self.env["fsm.route.dayroute"])

    def test_route_worker_change_updates_order_person(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
            }
        )
        self.assertEqual(order.person_id, self.test_person)
        other_person = self.env["fsm.person"].create({"name": "New Route Worker"})
        self.fsm_route_id.fsm_person_id = other_person
        self.assertEqual(order.person_id, other_person)

    def test_dayroute_uses_worker_local_date(self):
        tuesday_day = self.env.ref("fieldservice_route.fsm_route_day_1")
        self.fsm_route_id.day_ids = [(6, 0, [tuesday_day.id])]
        self.test_person.partner_id.tz = "America/Toronto"
        route_date = self.date.date()
        while route_date.weekday() != 1:
            route_date += timedelta(days=1)
        local_start = timezone("America/Toronto").localize(
            datetime.combine(
                route_date, datetime.min.time().replace(hour=23, minute=30)
            )
        )
        utc_start = local_start.astimezone(utc).replace(tzinfo=None)
        self.assertNotEqual(utc_start.date(), route_date)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": utc_start,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.dayroute_id.date, route_date)

    def test_create_with_dayroute_syncs_person_and_schedule(self):
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "dayroute_id": dayroute.id,
            }
        )
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.person_id, dayroute.person_id)
        self.assertEqual(order.scheduled_date_start, dayroute.date_start_planned)

    def test_create_with_mismatched_dayroute_raises(self):
        other_route = self.fsm_route_obj.create(
            {
                "name": "Create Mismatch Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": other_route.id,
                "date": self.date.date(),
            }
        )
        with self.assertRaises(ValidationError):
            self.env["fsm.order"].create(
                {
                    "location_id": self.test_location.id,
                    "dayroute_id": dayroute.id,
                }
            )

    def test_write_dayroute_overrides_conflicting_person_and_date(self):
        self.test_person.partner_id.tz = "UTC"
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date.replace(hour=10, minute=0),
                "person_id": self.test_person.id,
            }
        )
        other_person = self.env["fsm.person"].create({"name": "Conflicting Worker"})
        other_person.partner_id.tz = "UTC"
        new_date = self.date.date() + timedelta(days=7)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        new_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": new_date,
            }
        )
        conflicting_start = self.date.replace(hour=15, minute=0)
        order.write(
            {
                "dayroute_id": new_dayroute.id,
                "person_id": other_person.id,
                "scheduled_date_start": conflicting_start,
            }
        )
        self.assertEqual(order.dayroute_id, new_dayroute)
        self.assertEqual(order.person_id, new_dayroute.person_id)
        self.assertNotEqual(order.person_id, other_person)
        local_date = order._local_date_from_scheduled_start(
            order.scheduled_date_start,
            person=order.person_id,
            route=order.fsm_route_id,
        )
        self.assertEqual(local_date, new_dayroute.date)
        self.assertEqual(order.scheduled_date_start.hour, 15)

    def test_dayroute_move_preserves_local_time_across_dst(self):
        self.test_person.partner_id.tz = "America/Toronto"
        tzinfo = timezone("America/Toronto")
        july_date = datetime(2026, 7, 14).date()
        january_date = datetime(2026, 1, 13).date()
        local_start = tzinfo.localize(
            datetime.combine(july_date, datetime.min.time().replace(hour=10))
        )
        utc_start = local_start.astimezone(utc).replace(tzinfo=None)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": utc_start,
                "scheduled_duration": 2.0,
                "person_id": self.test_person.id,
            }
        )
        january_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": january_date,
            }
        )
        order.write({"dayroute_id": january_dayroute.id})
        local_after = utc.localize(order.scheduled_date_start).astimezone(tzinfo)
        self.assertEqual(local_after.date(), january_date)
        self.assertEqual(local_after.hour, 10)
        self.assertEqual(order.scheduled_duration, 2.0)
        local_end = utc.localize(order.scheduled_date_end).astimezone(tzinfo)
        self.assertEqual(local_end.hour, 12)

    def test_reject_routed_order_on_routeless_dayroute(self):
        routeless_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "date": self.date.date(),
                "person_id": self.test_person.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        with self.assertRaises(ValidationError):
            order.write({"dayroute_id": routeless_dayroute.id})

    def test_reject_routeless_order_on_routed_dayroute(self):
        routeless_location = self.env["fsm.location"].create(
            {
                "name": "Routeless Order Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        routed_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        with self.assertRaises(ValidationError):
            self.env["fsm.order"].create(
                {
                    "location_id": routeless_location.id,
                    "dayroute_id": routed_dayroute.id,
                }
            )

    def test_route_worker_change_reassigns_dayroute_by_timezone(self):
        self.fsm_route_id.day_ids = [(6, 0, self.days)]
        self.test_person.partner_id.tz = "America/Toronto"
        # Tuesday 00:30 Toronto == Monday 21:30 Los Angeles
        tuesday = self.date.date()
        while tuesday.weekday() != 1:
            tuesday += timedelta(days=1)
        local_start = timezone("America/Toronto").localize(
            datetime.combine(tuesday, datetime.min.time().replace(hour=0, minute=30))
        )
        utc_start = local_start.astimezone(utc).replace(tzinfo=None)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": utc_start,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.dayroute_id.date, tuesday)
        la_person = self.env["fsm.person"].create({"name": "LA Worker"})
        la_person.partner_id.tz = "America/Los_Angeles"
        self.fsm_route_id.fsm_person_id = la_person
        self.assertEqual(order.person_id, la_person)
        la_date = order._local_date_from_scheduled_start(
            order.scheduled_date_start,
            person=la_person,
            route=self.fsm_route_id,
        )
        self.assertEqual(la_date, tuesday - timedelta(days=1))
        self.assertEqual(order.dayroute_id.date, la_date)
        self.assertEqual(order.dayroute_id.person_id, la_person)

    def test_write_dayroute_with_duration_keeps_positive_end(self):
        self.test_person.partner_id.tz = "UTC"
        start = datetime(2026, 1, 15, 9, 0, 0)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": start,
                "scheduled_duration": 2.0,
                "person_id": self.test_person.id,
            }
        )
        new_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": datetime(2026, 1, 22).date(),
            }
        )
        order.write(
            {
                "dayroute_id": new_dayroute.id,
                "scheduled_duration": 3.0,
            }
        )
        self.assertEqual(order.scheduled_date_start.date(), new_dayroute.date)
        self.assertEqual(order.scheduled_duration, 3.0)
        self.assertEqual(
            order.scheduled_date_end, order.scheduled_date_start + timedelta(hours=3)
        )
        self.assertGreater(order.scheduled_date_end, order.scheduled_date_start)

    def test_write_dayroute_keeps_end_aligned_with_duration(self):
        self.test_person.partner_id.tz = "UTC"
        start = datetime(2026, 1, 15, 9, 0, 0)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": start,
                "scheduled_duration": 2.0,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.scheduled_date_end, start + timedelta(hours=2))
        new_dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": datetime(2026, 1, 22).date(),
            }
        )
        order.write({"dayroute_id": new_dayroute.id})
        self.assertEqual(order.scheduled_date_start.hour, 9)
        self.assertEqual(order.scheduled_duration, 2.0)
        self.assertEqual(
            order.scheduled_date_end,
            order.scheduled_date_start + timedelta(hours=2),
        )

    def test_write_duration_on_full_dayroute_keeps_same_dayroute(self):
        route = self.fsm_route_obj.create(
            {
                "name": "Full Capacity Route",
                "max_order": 1,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        location = self.env["fsm.location"].create(
            {
                "name": "Full Capacity Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "scheduled_date_start": self.date,
                "scheduled_duration": 1.0,
                "person_id": self.test_person.id,
            }
        )
        dayroute = order.dayroute_id
        self.assertEqual(dayroute.order_remaining, 0)
        order.write({"scheduled_duration": 2.0})
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.scheduled_duration, 2.0)
        self.assertTrue(dayroute.exists())

    def test_fsm_user_can_create_dayroute_when_rescheduling(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        fsm_user = self.env["res.users"].create(
            {
                "name": "FSM Route User",
                "login": "fsm_route_dayroute_user",
                "group_ids": [(6, 0, [self.env.ref("fieldservice.group_fsm_user").id])],
            }
        )
        order.with_user(fsm_user).write(
            {
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertTrue(order.dayroute_id)
        self.assertEqual(order.dayroute_id.person_id, self.test_person)

    def test_create_with_dayroute_start_and_end_keeps_duration(self):
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
            }
        )
        start = datetime.combine(self.date.date(), datetime.min.time().replace(hour=9))
        end = start + timedelta(hours=2)
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "dayroute_id": dayroute.id,
                "scheduled_date_start": start,
                "scheduled_date_end": end,
            }
        )
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.scheduled_duration, 2.0)
        self.assertEqual(
            order.scheduled_date_end, order.scheduled_date_start + timedelta(hours=2)
        )
        self.assertNotEqual(order.scheduled_date_end, order.scheduled_date_start)

    def test_staffing_unstaffed_route_assigns_dayroute(self):
        route = self.fsm_route_obj.create(
            {
                "name": "Unstaffed Then Staffed",
                "max_order": 10,
                "day_ids": [(6, 0, self.days)],
            }
        )
        location = self.env["fsm.location"].create(
            {
                "name": "Unstaffed Route Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "scheduled_date_start": self.date,
            }
        )
        self.assertFalse(order.dayroute_id)
        route.fsm_person_id = self.test_person
        self.assertEqual(order.person_id, self.test_person)
        self.assertTrue(order.dayroute_id)
        self.assertEqual(order.dayroute_id.person_id, self.test_person)
        self.assertEqual(
            order.dayroute_id.date,
            order._local_date_from_scheduled_start(
                order.scheduled_date_start,
                person=order.person_id,
                route=route,
            ),
        )

    def test_write_person_false_clears_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        self.assertTrue(old_dayroute)
        order.write({"person_id": False})
        self.assertFalse(order.person_id)
        self.assertFalse(order.dayroute_id)
        self.assertFalse(old_dayroute.exists())

    def test_fsm_user_can_reschedule_existing_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        fsm_user = self.env["res.users"].create(
            {
                "name": "FSM Reschedule User",
                "login": "fsm_route_reschedule_user",
                "group_ids": [(6, 0, [self.env.ref("fieldservice.group_fsm_user").id])],
            }
        )
        new_date = self.date + timedelta(days=1)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        order.with_user(fsm_user).write({"scheduled_date_start": new_date})
        self.assertTrue(order.dayroute_id)
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertEqual(order.dayroute_id.date, new_date.date())
        self.assertFalse(old_dayroute.exists())

    def test_unstaffing_route_clears_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        self.fsm_route_id.fsm_person_id = False
        self.assertFalse(order.person_id)
        self.assertFalse(order.dayroute_id)
        self.assertFalse(old_dayroute.exists())

    def test_location_route_change_reassigns_dayroute(self):
        other_person = self.env["fsm.person"].create({"name": "Other Route Worker"})
        other_route = self.fsm_route_obj.create(
            {
                "name": "Location Change Target Route",
                "max_order": 10,
                "fsm_person_id": other_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        self.assertEqual(old_dayroute.route_id, self.fsm_route_id)
        self.test_location.fsm_route_id = other_route
        self.assertEqual(order.fsm_route_id, other_route)
        self.assertEqual(order.person_id, other_person)
        self.assertTrue(order.dayroute_id)
        self.assertEqual(order.dayroute_id.route_id, other_route)
        self.assertEqual(order.dayroute_id.person_id, other_person)
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_write_location_to_unstaffed_route_clears_dayroute(self):
        unstaffed_route = self.fsm_route_obj.create(
            {
                "name": "Unstaffed Target Route",
                "max_order": 10,
                "day_ids": [(6, 0, self.days)],
            }
        )
        unstaffed_location = self.env["fsm.location"].create(
            {
                "name": "Unstaffed Target Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": unstaffed_route.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        self.assertTrue(old_dayroute)
        order.write({"location_id": unstaffed_location.id})
        self.assertEqual(order.fsm_route_id, unstaffed_route)
        self.assertFalse(order.person_id)
        self.assertFalse(order.dayroute_id)
        self.assertFalse(old_dayroute.exists())
        stale = self.env["fsm.route.dayroute"].search(
            [
                ("route_id", "=", unstaffed_route.id),
                ("person_id", "=", self.test_person.id),
            ]
        )
        self.assertFalse(stale)

    def test_reschedule_keeps_manually_assigned_worker(self):
        other_person = self.env["fsm.person"].create({"name": "Manual Assignee"})
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        order.write({"person_id": other_person.id})
        self.assertEqual(order.person_id, other_person)
        self.assertEqual(order.dayroute_id.person_id, other_person)
        old_dayroute = order.dayroute_id
        new_date = self.date + timedelta(days=1)
        while new_date.weekday() > 4:
            new_date += timedelta(days=1)
        order.write({"scheduled_date_start": new_date})
        self.assertEqual(order.person_id, other_person)
        self.assertTrue(order.dayroute_id)
        self.assertEqual(order.dayroute_id.person_id, other_person)
        self.assertEqual(order.dayroute_id.date, new_date.date())
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertNotEqual(
            order.dayroute_id.person_id, self.fsm_route_id.fsm_person_id
        )

    def test_get_person_id_keeps_worker_when_moving_to_routeless(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        routeless_location = self.env["fsm.location"].create(
            {
                "name": "Routeless Move Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        person_id = order._get_person_id_for_dayroute(
            {"location_id": routeless_location.id}, False
        )
        self.assertEqual(person_id, self.test_person.id)

    def test_get_person_id_from_route_without_order_person(self):
        order = self.env["fsm.order"].new({})
        self.assertFalse(order.person_id)
        person_id = order._get_person_id_for_dayroute({}, self.fsm_route_id.id)
        self.assertEqual(person_id, self.test_person.id)

    def test_get_person_id_from_order_route_when_no_route_id(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        order.person_id = False
        person_id = order._get_person_id_for_dayroute({}, False)
        self.assertEqual(person_id, self.fsm_route_id.fsm_person_id.id)

    def test_local_date_from_scheduled_start_without_start(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        self.assertFalse(order._local_date_from_scheduled_start(False))
        self.assertFalse(order._local_date_from_scheduled_start(None))

    def test_duration_for_schedule_sync_from_start_and_end(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        start = self.date.replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=2)
        duration = order._duration_for_schedule_sync(
            {
                "scheduled_date_start": start,
                "scheduled_date_end": end,
            }
        )
        self.assertEqual(duration, 2.0)

    def test_sync_scheduled_end_without_start_returns_vals(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        vals = {"scheduled_duration": 1.0}
        self.assertEqual(order._sync_scheduled_end_from_start(vals), vals)

    def test_reassign_dayroute_skips_unscheduled_order(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
            }
        )
        self.assertFalse(order.scheduled_date_start)
        self.assertFalse(order.dayroute_id)
        order._reassign_dayroute_for_person_timezone()
        self.assertFalse(order.dayroute_id)

    def test_reassign_dayroute_keeps_matching_dayroute(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        dayroute = order.dayroute_id
        order._reassign_dayroute_for_person_timezone()
        self.assertEqual(order.dayroute_id, dayroute)

    def test_prepare_vals_from_dayroute_without_person_or_date(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        dayroute = self.env["fsm.route.dayroute"].new(
            {
                "route_id": self.fsm_route_id.id,
                "person_id": False,
                "date": False,
                "team_id": False,
            }
        )
        vals = order._prepare_vals_from_dayroute(dayroute, {"description": "x"})
        self.assertEqual(vals, {"description": "x"})
        self.assertNotIn("person_id", vals)
        self.assertNotIn("team_id", vals)
        self.assertNotIn("scheduled_date_start", vals)

    def test_write_location_to_routeless_keeps_worker_dayroute(self):
        routeless_location = self.env["fsm.location"].create(
            {
                "name": "Routeless Write Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        old_dayroute = order.dayroute_id
        order.write({"location_id": routeless_location.id})
        self.assertFalse(order.fsm_route_id)
        self.assertEqual(order.person_id, self.test_person)
        self.assertTrue(order.dayroute_id)
        self.assertEqual(order.dayroute_id.person_id, self.test_person)
        self.assertFalse(order.dayroute_id.route_id)
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())

    def test_tz_name_falls_back_to_utc(self):
        order = self.env["fsm.order"].new({})
        person = self.env["fsm.person"].create({"name": "No TZ Worker"})
        person.partner_id.tz = False
        person.calendar_id = False
        old_tz = self.env.user.tz
        self.env.user.tz = False
        try:
            self.assertEqual(
                order._tz_name_for_route_day(
                    person=person, route=self.env["fsm.route"]
                ),
                "UTC",
            )
        finally:
            self.env.user.tz = old_tz

    def test_tz_name_uses_worker_calendar_before_user(self):
        """Partner without tz must use the worker calendar tz, not the user."""
        order = self.env["fsm.order"].new({})
        calendar = self.env["resource.calendar"].create(
            {
                "name": "LA Calendar",
                "tz": "America/Los_Angeles",
            }
        )
        person = self.env["fsm.person"].create({"name": "Calendar TZ Worker"})
        person.partner_id.tz = False
        person.calendar_id = calendar
        old_tz = self.env.user.tz
        self.env.user.tz = "UTC"
        try:
            self.assertEqual(
                order._tz_name_for_route_day(
                    person=person, route=self.env["fsm.route"]
                ),
                "America/Los_Angeles",
            )
            # Near midnight: UTC morning is still the previous day in LA.
            utc_start = datetime(2026, 7, 28, 2, 0, 0)
            self.assertEqual(
                order._local_date_from_scheduled_start(
                    utc_start, person=person, route=self.env["fsm.route"]
                ),
                datetime(2026, 7, 27).date(),
            )
        finally:
            self.env.user.tz = old_tz

    def test_write_direct_dayroute_syncs_team(self):
        """Assigning a day route must align the order team with the day route."""
        company_b = self.env["res.company"].create({"name": "Dayroute Team Co"})
        team_a = self.env["fsm.team"].search(
            [("company_id", "in", (self.env.company.id, False))],
            order="sequence asc",
            limit=1,
        )
        team_b = self.env["fsm.team"].create(
            {
                "name": "Other Dayroute Team",
                "company_id": company_b.id,
            }
        )
        dayroute = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
                "person_id": self.test_person.id,
                "team_id": team_b.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "team_id": team_a.id,
            }
        )
        self.assertEqual(order.team_id, team_a)
        order.write({"dayroute_id": dayroute.id})
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(order.team_id, team_b)

    def test_capture_duration_skips_when_duration_present(self):
        order = self.env["fsm.order"].new({"location_id": self.test_location.id})
        start = self.date.replace(hour=9, minute=0, second=0, microsecond=0)
        vals = {
            "scheduled_duration": 4.0,
            "scheduled_date_start": start,
            "scheduled_date_end": start + timedelta(hours=1),
        }
        result = order._capture_duration_from_start_end(vals)
        self.assertEqual(result["scheduled_duration"], 4.0)

    def test_route_id_changing_false_when_same_route(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertFalse(
            order._route_id_changing(
                {"location_id": self.test_location.id}, self.fsm_route_id.id
            )
        )

    def test_dayroute_uses_order_team_not_active_company(self):
        """Scheduling a Company B order must not reuse Company A's day route."""
        company_a = self.env.company
        company_b = self.env["res.company"].create({"name": "Route Company B"})
        calendar_b = self.env["resource.calendar"].create(
            {
                "name": "Company B Calendar",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Early Shift",
                            "dayofweek": str(self.date.weekday()),
                            "hour_from": 5.0,
                            "hour_to": 13.0,
                            "day_period": "morning",
                        },
                    )
                ],
            }
        )
        company_b.resource_calendar_id = calendar_b
        team_a = self.env["fsm.team"].search(
            [("company_id", "in", (company_a.id, False))],
            order="sequence asc",
            limit=1,
        )
        team_b = self.env["fsm.team"].create(
            {
                "name": "Company B Team",
                "company_id": company_b.id,
            }
        )
        self.test_person.calendar_id = False
        dayroute_a = self.env["fsm.route.dayroute"].create(
            {
                "route_id": self.fsm_route_id.id,
                "date": self.date.date(),
                "person_id": self.test_person.id,
                "team_id": team_a.id,
            }
        )
        location_b = self.env["fsm.location"].create(
            {
                "name": "Company B Route Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": self.fsm_route_id.id,
                "team_id": team_b.id,
            }
        )
        # Active company remains Company A while creating a Company B order.
        order = self.env["fsm.order"].create(
            {
                "location_id": location_b.id,
                "team_id": team_b.id,
                "scheduled_date_start": self.date,
                "person_id": self.test_person.id,
            }
        )
        self.assertEqual(order.team_id, team_b)
        self.assertTrue(order.dayroute_id)
        self.assertNotEqual(order.dayroute_id, dayroute_a)
        self.assertEqual(order.dayroute_id.team_id, team_b)
        self.assertEqual(order.dayroute_id.date_start_planned.hour, 5)
