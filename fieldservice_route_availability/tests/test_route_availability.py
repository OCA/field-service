# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestRouteAvailability(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_person = cls.env.ref("fieldservice.test_person")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.blackout_group = cls.env["fsm.blackout.group"].create(
            {
                "name": "Test Blackout Group",
                "fsm_blackout_day_ids": [
                    (0, 0, {"name": "Test Blackout Day", "date": fields.Date.today()})
                ],
            }
        )

        cls.days = [
            cls.env.ref("fieldservice_route.fsm_route_day_0").id,
            cls.env.ref("fieldservice_route.fsm_route_day_1").id,
            cls.env.ref("fieldservice_route.fsm_route_day_2").id,
            cls.env.ref("fieldservice_route.fsm_route_day_3").id,
            cls.env.ref("fieldservice_route.fsm_route_day_4").id,
            cls.env.ref("fieldservice_route.fsm_route_day_5").id,
            cls.env.ref("fieldservice_route.fsm_route_day_6").id,
        ]
        cls.fsm_route_id = cls.env["fsm.route"].create(
            {
                "name": "Demo Route",
                "max_order": 10,
                "fsm_person_id": cls.test_person.id,
                "day_ids": [(6, 0, cls.days)],
            }
        )
        cls.test_location.fsm_route_id = cls.fsm_route_id.id
        cls.fsm_route_id.fsm_blackout_group_ids = [cls.blackout_group.id]

    def test_validate_blackout_days(self):
        order_form = Form(self.env["fsm.order"])
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = fields.Datetime.today()
        with self.assertRaises(ValidationError):
            order_form.save()
        order_form.scheduled_date_start = fields.Datetime.today() + timedelta(days=1)
        self.assertTrue(order_form.save())

    def test_validate_blackout_days_with_zip(self):
        self.blackout_group.fsm_blackout_day_ids[0].zip = "12345"

        self.test_location.zip = "12345"
        order_form = Form(self.env["fsm.order"])
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = fields.Datetime.today()
        with self.assertRaises(ValidationError):
            order_form.save()

        self.test_location.zip = "99999"
        order_form = Form(self.env["fsm.order"])
        order_form.location_id = self.test_location
        order_form.scheduled_date_start = fields.Datetime.today()
        self.assertTrue(order_form.save())
