# Copyright (C) 2012 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFsmLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.FSMLocation = cls.env["fsm.location"]
        cls.location_partner_1 = cls.env.ref("fieldservice.location_partner_1")
        cls.location_partner_2 = cls.env.ref("fieldservice.location_partner_2")
        cls.location_partner_3 = cls.env.ref("fieldservice.location_partner_3")
        cls.test_loc_partner = cls.env.ref("fieldservice.test_loc_partner")
        # delta value of 0.00001 was chosen according to
        # OpenStreetMap's decimal precision table
        # https://wiki.openstreetmap.org/wiki/Precision_of_coordinates#Conversion_to_decimal
        # 5 decimals are necessary for precision of about a metre
        cls.delta = 0.000_01

        cls.test_location = cls.FSMLocation.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "test@example.com",
                "partner_id": cls.location_partner_1.id,
                "owner_id": cls.location_partner_2.id,
            }
        )

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_fsm_location_creation(self):
        test_partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        # should not be localized yet
        test_partner.write(
            {
                "street": "Rue des Bourlottes 9",
                "zip": "1367",
                "city": "Grand-Rosière",
                "country_id": self.env.ref("base.be"),
            }
        )
        self.assertFalse(self.location_partner_1.partner_latitude)
        self.assertFalse(self.location_partner_1.partner_longitude)
        # should be localized after assigning a partner to the location
        test_location_1 = self.FSMLocation.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "test@example.com",
                "partner_id": test_partner.id,
                "owner_id": self.location_partner_1.id,
            }
        )
        self.assertTrue(test_location_1.partner_latitude)
        self.assertTrue(test_location_1.partner_longitude)
        self.assertAlmostEqual(
            test_location_1.partner_latitude, 50.629980, delta=0.0002
        )
        self.assertAlmostEqual(
            test_location_1.partner_longitude, 4.863370, delta=0.00012
        )
        # direct creation and same exit data
        partner_latitude = 1.0
        partner_longitude = 2.0
        test_location_2 = self.FSMLocation.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "test@example.com",
                "partner_id": self.location_partner_1.id,
                "owner_id": self.location_partner_2.id,
                "partner_latitude": partner_latitude,
                "partner_longitude": partner_longitude,
            }
        )
        self.assertTrue(test_location_2.shape)
        self.assertAlmostEqual(
            test_location_2.partner_latitude, partner_latitude, delta=self.delta
        )
        self.assertAlmostEqual(
            test_location_2.partner_longitude, partner_longitude, delta=self.delta
        )

    def test_fsm_location_update(self):
        # update both coordinates
        self.test_location.write(
            {
                "date_localization": fields.Datetime.today(),
                "partner_latitude": 1.00,
                "partner_longitude": 2.00,
            }
        )
        self.assertTrue(self.test_location.partner_latitude)
        self.assertTrue(self.test_location.partner_longitude)
        self.assertTrue(self.test_location.shape)
        # update a single coordinate (latitude)
        new_latitude = 1.00
        old_longitude = self.test_location.partner_longitude
        self.test_location.write(
            {
                "partner_latitude": new_latitude,
            }
        )
        self.assertEqual(self.test_location.partner_latitude, new_latitude)
        self.assertEqual(self.test_location.partner_longitude, old_longitude)
        # update a single coordinate (longitude)
        new_longitude = 7.00
        old_latitude = self.test_location.partner_latitude
        self.test_location.write(
            {
                "partner_longitude": new_longitude,
            }
        )
        self.assertAlmostEqual(
            self.test_location.partner_longitude, new_longitude, delta=self.delta
        )
        self.assertEqual(self.test_location.partner_latitude, old_latitude)

    def test_fsm_location_association(self):
        test_location = self.FSMLocation.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "test@example.com",
                "partner_id": self.location_partner_1.id,
                "owner_id": self.location_partner_2.id,
                "partner_latitude": 1.0,
                "partner_longitude": 2.0,
            }
        )
        fsm_order = self.env["fsm.order"].create({"location_id": test_location.id})
        self.assertTrue(fsm_order.shape)
        self.assertEqual(fsm_order.shape, test_location.shape)
        # geolocalize method
        fsm_order.geo_localize()
        self.assertTrue(fsm_order.location_id)
        # fsm_order should point to the same location
        test_location.write(
            {
                "partner_latitude": 4.00,
                "partner_longitude": 3.00,
            }
        )
        self.assertEqual(fsm_order.shape, test_location.shape)
        test_location.partner_latitude = False
        self.assertTrue(test_location.shape)
        test_location.partner_longitude = False
        self.assertFalse(test_location.shape)
