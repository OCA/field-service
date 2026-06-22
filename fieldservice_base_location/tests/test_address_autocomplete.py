import requests

from odoo.tests.common import TransactionCase


class TestFsmLocationZipSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.country = cls.env.ref("base.us")
        cls.state = cls.env.ref("base.state_us_1")
        cls.city = cls.env["res.city"].create(
            {
                "name": "Sample City",
                "state_id": cls.state.id,
                "country_id": cls.country.id,
            }
        )

        cls.res_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.zip_record = cls.env["res.city.zip"].create(
            {
                "name": "07001",
                "city_id": cls.city.id,
            }
        )
        cls.zip_record_other = cls.env["res.city.zip"].create(
            {
                "name": "99999",
                "city_id": cls.city.id,
            }
        )

        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "partner_id": cls.res_partner.id,
                "zip": "07001",
                "zip_id": cls.zip_record.id,
                "owner_id": cls.res_partner.id,
            }
        )

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_zip_id_mismatch_resets_zip_id(self):
        """Should reset zip_id if it doesn't match zip"""
        self.location.write({"zip": "99999"})
        self.assertFalse(self.location.zip_id, "zip_id should be reset to False")
        self.assertFalse(self.res_partner.zip_id, "Partner zip_id should also be reset")

    def test_zip_id_match_keeps_zip_id(self):
        """Should keep zip_id if zip matches zip_id.name"""
        self.location.write({"zip": "07001"})
        self.assertEqual(
            self.location.zip_id, self.zip_record, "zip_id should remain unchanged"
        )

    def test_partner_fields_synced(self):
        """Should sync fields like zip, city, state_id, etc. to partner"""
        state = self.env.ref("base.state_us_1")
        country = self.env.ref("base.us")

        self.location.write(
            {
                "zip": "12345",
                "city": "Test City",
                "state_id": state.id,
                "country_id": country.id,
                "street": "Main St",
                "street2": "Apt 42",
            }
        )

        partner = self.location.partner_id
        self.assertEqual(partner.zip, "12345")
        self.assertEqual(partner.city, "Test City")
        self.assertEqual(partner.state_id, state)
        self.assertEqual(partner.country_id, country)
        self.assertEqual(partner.street, "Main St")
        self.assertEqual(partner.street2, "Apt 42")

    def test_no_partner_does_not_fail(self):
        """Should not fail if location has no partner"""
        location = self.env["fsm.location"].create(
            {
                "name": "Orphan Location",
                "zip": "07001",
                "zip_id": self.zip_record.id,
                "owner_id": self.res_partner.id,
            }
        )
        location.write({"zip": "99999"})
        self.assertFalse(location.zip_id)
