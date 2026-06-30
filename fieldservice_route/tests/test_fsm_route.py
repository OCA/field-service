# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMRoute(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Route = cls.env["fsm.route"]
        cls.DayRoute = cls.env["fsm.route.dayroute"]
        cls.monday = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.tuesday = cls.env.ref("fieldservice_route.fsm_route_day_1")
        cls.route = cls.Route.create(
            {
                "name": "Weekday Route",
                "max_order": 2,
                "fsm_person_id": cls.test_person.id,
                "day_ids": [(6, 0, [cls.monday.id, cls.tuesday.id])],
            }
        )

    def _next_weekday(self, weekday):
        date = datetime.now().date()
        while date.weekday() != weekday:
            date += timedelta(days=1)
        return date

    def test_run_on_scheduled_day(self):
        monday = self._next_weekday(0)
        self.assertTrue(self.route.run_on(monday))

    def test_run_on_non_scheduled_day(self):
        wednesday = self._next_weekday(2)
        self.assertFalse(self.route.run_on(wednesday))

    def test_run_on_no_date(self):
        self.assertFalse(self.route.run_on(False))

    def test_dayroute_sequence_name(self):
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": self._next_weekday(0),
            }
        )
        self.assertTrue(dayroute.name.startswith("SR"))

    def test_dayroute_person_from_route(self):
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": self._next_weekday(0),
            }
        )
        self.assertEqual(dayroute.person_id, self.route.fsm_person_id)

    def test_dayroute_order_count(self):
        route_date = self._next_weekday(0)
        self.test_location.fsm_route_id = self.route
        dayroute = self.DayRoute.create(
            {
                "route_id": self.route.id,
                "date": route_date,
            }
        )
        self.assertEqual(dayroute.order_count, 0)
        self.assertEqual(dayroute.order_remaining, self.route.max_order)
        self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": datetime.combine(
                    route_date, datetime.min.time()
                ),
                "person_id": self.test_person.id,
                "dayroute_id": dayroute.id,
            }
        )
        dayroute.invalidate_recordset()
        self.assertEqual(dayroute.order_count, 1)
        self.assertEqual(dayroute.order_remaining, 1)

    def test_dayroute_check_day_constraint(self):
        wednesday = self._next_weekday(2)
        with self.assertRaises(ValidationError):
            self.DayRoute.create(
                {
                    "route_id": self.route.id,
                    "date": wednesday,
                }
            )

    def test_dayroute_check_capacity_constraint(self):
        route = self.Route.create(
            {
                "name": "Single Order Route",
                "max_order": 1,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, [self.monday.id])],
            }
        )
        route_date = self._next_weekday(0)
        location = self.env["fsm.location"].create(
            {
                "name": "Capacity Route Location",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "fsm_route_id": route.id,
            }
        )
        dayroute = self.DayRoute.create(
            {
                "route_id": route.id,
                "date": route_date,
            }
        )
        self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "dayroute_id": dayroute.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["fsm.order"].create(
                {
                    "location_id": location.id,
                    "dayroute_id": dayroute.id,
                }
            )
