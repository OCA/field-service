# Copyright (C) 2012 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFsmLocation(TransactionCase):
    def setUp(self):
        super(TestFsmLocation, self).setUp()
        self.fsm_location = self.env["fsm.location"]
        self.location_partner_1 = self.env.ref("fieldservice.location_partner_1")
        self.location_partner_2 = self.env.ref("fieldservice.location_partner_2")
        self.test_loc_partner = self.env.ref("fieldservice.test_loc_partner")
        self.location_partner_3 = self.env.ref("fieldservice.location_partner_3")

    def test_fsm_location(self):
        test_location = self.fsm_location.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "tl@email.com",
                "partner_id": self.location_partner_1.id,
                "owner_id": self.location_partner_2.id,
            }
        )
        self.assertTrue(test_location.shape)
        fsm_order = self.env["fsm.order"].create({"location_id": test_location.id})
        test_location.write(
            {
                "date_localization": fields.Datetime.today(),
                "partner_latitude": 1.00,
                "partner_longitude": 2.00,
            }
        )
        self.assertTrue(test_location.partner_latitude)
        self.assertTrue(test_location.partner_longitude)
        self.assertTrue(test_location.shape)
        fsm_order.geo_localize()

        self.test_loc_partner.partner_latitude = 1.0
        self.test_loc_partner.partner_longitude = 2.0
        test_location1 = self.fsm_location.create(
            {
                "name": "Test Location 3",
                "phone": "1234",
                "email": "tl1@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.location_partner_3.id,
            }
        )
        self.assertTrue(test_location1.shape)
