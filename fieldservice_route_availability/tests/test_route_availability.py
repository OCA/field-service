# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestRouteAvailability(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Order = cls.env["fsm.order"]
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

    def test_blackout_day_validation(self):
        with self.assertRaisesRegex(ValidationError, r"The date .+ is a blackout day"):
            self.Order.create(
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": fields.Datetime.now(),
                }
            )

        self.assertTrue(
            self.Order.create(
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": fields.Datetime.now() + timedelta(days=1),
                }
            )
        )

    def test_blackout_day_with_zip(self):
        self.blackout_group.fsm_blackout_day_ids[0].zip = "12345"
        self.test_location.zip = "12345"

        with self.assertRaisesRegex(ValidationError, r"The date .+ is a blackout day"):
            self.Order.create(
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": fields.Datetime.now(),
                }
            )

        self.test_location.zip = "99999"
        self.assertTrue(
            self.Order.create(
                {
                    "location_id": self.test_location.id,
                    "scheduled_date_start": fields.Datetime.now(),
                }
            )
        )
