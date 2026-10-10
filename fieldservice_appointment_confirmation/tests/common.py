# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.addons.base.tests.common import BaseCommon


class FieldServiceAppointmentCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {"name": "Appointment Test Customer", "email": "customer@example.com"}
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Appointment Test Location",
                "owner_id": cls.customer.id,
                "partner_id": cls.customer.id,
            }
        )
        cls.calendar = cls.env.company.resource_calendar_id
        cls.person = cls.env["fsm.person"].create(
            {"name": "Appointment Worker", "calendar_id": cls.calendar.id}
        )
        cls.stage_open = cls.env["fsm.stage"].create(
            {
                "name": "Scheduled (test)",
                "stage_type": "order",
                "sequence": 9001,
                "allow_confirmation_request": True,
            }
        )
        cls.start = datetime.now().replace(
            hour=10, minute=0, second=0, microsecond=0
        ) + timedelta(days=7)
        cls.order = cls._create_order(cls.start)

    @classmethod
    def _create_order(cls, start, duration=1.0, stage=None, **vals):
        return cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
                "person_id": cls.person.id,
                "stage_id": (stage or cls.stage_open).id,
                "scheduled_date_start": start,
                "scheduled_duration": duration,
                **vals,
            }
        )
