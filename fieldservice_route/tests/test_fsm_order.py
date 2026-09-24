# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class FSMOrderRouteCase(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.fsm_stage_obj = self.env["fsm.stage"]
        self.fsm_order_obj = self.env["fsm.order"]
        self.fsm_route_obj = self.env["fsm.route"]
        self.fsm_dayroute_obj = self.env["fsm.route.dayroute"]
        self.test_person = self.env.ref("fieldservice.test_person")
        self.test_location = self.env.ref("fieldservice.test_location")
        date = datetime.now()
        self.date = date.replace(microsecond=0)
        self.days = [
            self.env.ref("fieldservice_route.fsm_route_day_0").id,
            self.env.ref("fieldservice_route.fsm_route_day_1").id,
            self.env.ref("fieldservice_route.fsm_route_day_2").id,
            self.env.ref("fieldservice_route.fsm_route_day_3").id,
            self.env.ref("fieldservice_route.fsm_route_day_4").id,
            self.env.ref("fieldservice_route.fsm_route_day_5").id,
            self.env.ref("fieldservice_route.fsm_route_day_6").id,
        ]
        self.fsm_route_id = self.fsm_route_obj.create(
            {
                "name": "Demo Route",
                "max_order": 10,
                "fsm_person_id": self.test_person.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        self.test_location.fsm_route_id = self.fsm_route_id.id

    def _create_order(self, location=None, person=None, date=None):
        """Create an order the same way the web Form does: with
        ``person_id``/``fsm_route_id`` already resolved in ``vals``, so
        ``create()`` manages the dayroute (mirrors what onchange does when
        creating through the UI, see ``test_create_day_route``)."""
        location = location or self.test_location
        person = person or self.test_person
        date = date or self.date
        return self.fsm_order_obj.create(
            {
                "location_id": location.id,
                "fsm_route_id": location.fsm_route_id.id,
                "person_id": person.id,
                "scheduled_date_start": date,
            }
        )

    def test_create_day_route(self):
        order_form = Form(self.fsm_order_obj)
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = self.date
        order = order_form.save()
        self.assertEqual(order.person_id, self.test_person)
        self.assertEqual(order.fsm_route_id, self.test_location.fsm_route_id)
        self.assertEqual(order.dayroute_id.person_id, order.person_id)
        self.assertEqual(order.dayroute_id.date, order.scheduled_date_start.date())
        self.assertEqual(order.dayroute_id.route_id, order.fsm_route_id)

    def test_write_unrelated_field_keeps_dayroute(self):
        """A write() that doesn't touch person/date/route must not
        re-trigger dayroute management (bug A). With the route already at
        capacity, re-running the search on every write kicks the order out
        into a brand new dayroute and orphans the original one — the exact
        duplicate reported in production, e.g. from the writes
        ``fieldservice_calendar`` performs right after create()."""
        self.fsm_route_id.max_order = 1
        order = self._create_order()
        dayroute = order.dayroute_id
        order.write({"description": "<p>irrelevant change</p>"})
        self.assertEqual(order.dayroute_id, dayroute)
        self.assertEqual(
            self.fsm_dayroute_obj.search_count(
                [
                    ("person_id", "=", self.test_person.id),
                    ("date", "=", self.date.date()),
                ]
            ),
            1,
        )

    def test_two_orders_same_day_share_dayroute(self):
        """Two orders for the same technician and day must share a single
        dayroute (the core of P0 #4)."""
        order1 = self._create_order()
        order2 = self._create_order()
        self.assertEqual(order1.dayroute_id, order2.dayroute_id)
        self.assertEqual(
            self.fsm_dayroute_obj.search_count(
                [
                    ("person_id", "=", self.test_person.id),
                    ("date", "=", self.date.date()),
                ]
            ),
            1,
        )

    def test_change_date_moves_and_cleans_dayroute(self):
        """Moving the only order of a dayroute to another day must create/
        reuse the dayroute of the new day and delete the now-empty old one
        (bug B: the cleanup must happen after the order is actually moved)."""
        order = self._create_order()
        old_dayroute = order.dayroute_id
        new_date = self.date + timedelta(days=1)
        order.write({"scheduled_date_start": new_date})
        self.assertNotEqual(order.dayroute_id, old_dayroute)
        self.assertFalse(old_dayroute.exists())
        self.assertEqual(order.dayroute_id.date, new_date.date())

    def test_change_date_keeps_nonempty_dayroute(self):
        """Moving one of several orders off a dayroute must not delete it
        while orders remain."""
        order1 = self._create_order()
        order2 = self._create_order()
        old_dayroute = order1.dayroute_id
        new_date = self.date + timedelta(days=1)
        order1.write({"scheduled_date_start": new_date})
        self.assertTrue(old_dayroute.exists())
        self.assertEqual(old_dayroute.order_ids, order2)

    def test_multi_record_write_no_cross_contamination(self):
        """A single write() on a recordset mixing orders of different
        technicians must resolve the dayroute of each record independently
        (bug A: the shared/mutated ``vals`` dict made every record end up
        pointing at the last computed dayroute)."""
        person2 = self.env["fsm.person"].create({"name": "Test Person 2"})
        location2 = self.env.ref("fieldservice.location_1")
        route2 = self.fsm_route_obj.create(
            {
                "name": "Demo Route 2",
                "max_order": 10,
                "fsm_person_id": person2.id,
                "day_ids": [(6, 0, self.days)],
            }
        )
        location2.fsm_route_id = route2.id

        order1 = self._create_order()
        order2 = self._create_order(location=location2, person=person2)
        new_date = self.date + timedelta(days=1)

        (order1 | order2).write({"scheduled_date_start": new_date})

        self.assertEqual(order1.dayroute_id.person_id, self.test_person)
        self.assertEqual(order2.dayroute_id.person_id, person2)
        self.assertEqual(order1.dayroute_id.date, new_date.date())
        self.assertEqual(order2.dayroute_id.date, new_date.date())
        self.assertNotEqual(order1.dayroute_id, order2.dayroute_id)

    def test_max_order_respected(self):
        """With a finite capacity, a full dayroute must not accept more
        orders: new orders open a new dayroute, and forcing one into the
        full dayroute must raise (bug C: with a real capacity limit, the
        domain must still find/refuse dayroutes correctly)."""
        self.fsm_route_id.max_order = 1
        order1 = self._create_order()
        order2 = self._create_order()
        self.assertNotEqual(order1.dayroute_id, order2.dayroute_id)
        with self.assertRaises(ValidationError):
            order2.dayroute_id = order1.dayroute_id.id

    def test_max_order_zero_unlimited(self):
        """``max_order = 0`` must mean "no limit": several orders for the
        same technician/day must all land on the same single dayroute
        without raising (bug C)."""
        self.fsm_route_id.max_order = 0
        orders = self.fsm_order_obj
        for _i in range(3):
            orders |= self._create_order()
        dayroutes = orders.mapped("dayroute_id")
        self.assertEqual(len(dayroutes), 1)
        self.assertEqual(
            self.fsm_dayroute_obj.search_count(
                [
                    ("person_id", "=", self.test_person.id),
                    ("date", "=", self.date.date()),
                ]
            ),
            1,
        )

    def test_unassign_clears_dayroute(self):
        """Unassigning an order (clearing both technician and scheduled
        date, as the auto-reschedule cron of the downstream product does)
        must detach it from its dayroute and delete the dayroute if it was
        the last order left in it (bug D)."""
        order = self._create_order()
        dayroute = order.dayroute_id
        self.assertTrue(dayroute)
        order.write({"person_id": False, "scheduled_date_start": False})
        self.assertFalse(order.dayroute_id)
        self.assertFalse(dayroute.exists())
