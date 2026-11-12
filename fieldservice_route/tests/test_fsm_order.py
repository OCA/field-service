# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import pytz

from odoo.tests import Form, common


class FSMOrderRouteCase(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.fsm_stage_obj = self.env["fsm.stage"]
        self.fsm_order_obj = self.env["fsm.order"]
        self.fsm_route_obj = self.env["fsm.route"]
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

    def test_create_day_route(self):
        order_form = Form(self.fsm_order_obj)
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = self.date
        order = order_form.save()
        self.assertEqual(order.person_id, self.test_person)
        self.assertEqual(order.fsm_route_id, self.test_location.fsm_route_id)
        self.assertEqual(order.dayroute_id.person_id, order.person_id)
        tz = pytz.timezone(order.env.user.tz or "UTC")
        expected_date = (
            pytz.utc.localize(order.scheduled_date_start).astimezone(tz).date()
        )
        self.assertEqual(order.dayroute_id.date, expected_date)
        self.assertEqual(order.dayroute_id.route_id, order.fsm_route_id)
