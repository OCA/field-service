# Copyright (C) 2012 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.base_geolocalize.models.base_geocoder import GeoCoder

GEOCODER_COORDINATES = (50.123_456, 4.123_456)


class TestFsmLocation(TransactionCase):
    @staticmethod
    def _geocode(addr, **kw):
        return GEOCODER_COORDINATES if addr else None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        geocoder_patch = patch.object(
            GeoCoder, "_call_openstreetmap", side_effect=cls._geocode
        )
        geocoder_patch.start()
        cls.addClassCleanup(geocoder_patch.stop)
        cls.FSMLocation = cls.env["fsm.location"]
        cls.location_partner_1 = cls.env.ref("fieldservice.location_partner_1")
        cls.location_partner_2 = cls.env.ref("fieldservice.location_partner_2")
        cls.location_partner_3 = cls.env.ref("fieldservice.location_partner_3")
        cls.test_loc_partner = cls.env.ref("fieldservice.test_loc_partner")
        # delta absorbs the rounding of the stored float value, which comes
        # from GEOCODER_COORDINATES
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
            test_location_1.partner_latitude,
            GEOCODER_COORDINATES[0],
            delta=self.delta,
        )
        self.assertAlmostEqual(
            test_location_1.partner_longitude,
            GEOCODER_COORDINATES[1],
            delta=self.delta,
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

    def test_multi_create(self):
        """Locations can be created in batch."""
        locations = self.FSMLocation.create(
            [
                {
                    "name": f"Test location {loc_index}",
                    "owner_id": self.location_partner_1.id,
                }
                for loc_index in range(2)
            ]
        )
        self.assertTrue(locations)
