# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class FSMVehicleCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_partner = self.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        self.test_vehicle = self.env["fsm.vehicle"].create({"name": "Test Vehicle"})

        self.test_worker = self.env["fsm.person"].create(
            {
                "name": "Test Wokrer",
                "email": "tw@email.com",
                "vehicle_id": self.test_vehicle.id,
            }
        )
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_partner.id,
                "owner_id": self.test_partner.id,
            }
        )

    def test_vehicle(self):
        self.test_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "person_id": self.test_worker.id,
            }
        )
        self.test_order._onchange_person_id()
