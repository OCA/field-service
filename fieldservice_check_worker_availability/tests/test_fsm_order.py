from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Test Calendar",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        cls.person = cls.env["fsm.person"].create(
            {
                "name": "Test Person",
                "calendar_id": cls.calendar.id,
                "partner_id": cls.partner.id,
            }
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Person",
                "resource_id": cls.env["resource.resource"]
                .create(
                    {
                        "name": "Test Person",
                    }
                )
                .id,
                "work_contact_id": cls.partner.id,
            }
        )

        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "owner_id": cls.partner.id,
            }
        )

        cls.fsm_order = cls.env["fsm.order"].create(
            {
                "person_id": cls.person.id,
                "location_id": cls.location.id,
            }
        )

    def test_person_with_leave(self):
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Vacation",
                "resource_id": self.employee.resource_id.id,
                "date_from": "2025-10-10 08:00:00",
                "date_to": "2025-10-10 18:00:00",
                "calendar_id": self.calendar.id,
            }
        )

        with self.assertRaises(ValidationError):
            self.fsm_order.write({"scheduled_date_start": "2025-10-10 10:00:00"})

    def test_calendar_attendance(self):
        self.env["resource.calendar.attendance"].create(
            {
                "calendar_id": self.calendar.id,
                "dayofweek": "2",
                "hour_from": 9.0,
                "hour_to": 17.0,
                "name": "Test Wednesday",
            }
        )

        try:
            self.fsm_order.write(
                {
                    "scheduled_date_start": "2025-04-23 10:00:00",
                }
            )
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_fsm_order_ends_during_leave(self):
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Test Leave",
                "resource_id": self.employee.resource_id.id,
                "date_from": "2025-10-10 12:00:00",
                "date_to": "2025-10-10 18:00:00",
                "calendar_id": self.calendar.id,
            }
        )

        with self.assertRaises(ValidationError):
            self.fsm_order.write(
                {
                    "scheduled_date_start": "2025-10-10 11:00:00",
                    "scheduled_date_end": "2025-10-10 13:00:00",
                }
            )

    def test_calendar_attendance_exceeds_work_hours(self):
        self.env["resource.calendar.attendance"].create(
            {
                "calendar_id": self.calendar.id,
                "dayofweek": "0",
                "hour_from": 9.0,
                "hour_to": 17.0,
                "name": "Test Monday",
            }
        )

        with self.assertRaises(ValidationError):
            self.fsm_order.write(
                {
                    "scheduled_date_start": "2025-04-21 10:00:00",
                    "scheduled_duration": 8,
                }
            )
