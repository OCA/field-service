# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.addons.base.tests.common import BaseCommon


class FSMVehicleCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        cls.vehicle = cls.env["fsm.vehicle"].create({"name": "Test Vehicle"})
        cls.test_worker = cls.env["fsm.person"].create(
            {
                "name": "Test Worker",
                "email": "tw@email.com",
                "vehicle_id": cls.vehicle.id,
            }
        )
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_partner.id,
                "owner_id": cls.test_partner.id,
            }
        )

    def test_order_assigns_vehicle(self):
        test_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "person_id": self.test_worker.id,
            }
        )
        self.assertEqual(test_order.vehicle_id, self.vehicle)
