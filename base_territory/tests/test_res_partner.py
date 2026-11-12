from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartnerTerritory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.country_c1 = cls.env["res.country"].create(
            {"name": "Test Country 1", "code": "XA"}
        )
        cls.country_c2 = cls.env["res.country"].create(
            {"name": "Test Country 2", "code": "XB"}
        )
        cls.state_s1 = cls.env["res.country.state"].create(
            {"name": "Test State 1", "code": "SA", "country_id": cls.country_c1.id}
        )
        cls.state_s2 = cls.env["res.country.state"].create(
            {"name": "Test State 2", "code": "SB", "country_id": cls.country_c1.id}
        )
        cls.state_s3 = cls.env["res.country.state"].create(
            {"name": "Test State 3", "code": "SC", "country_id": cls.country_c2.id}
        )
        cls.region_r1 = cls.env["res.region"].create(
            {"name": "Test Region 1", "state_id": cls.state_s1.id}
        )
        cls.region_r2 = cls.env["res.region"].create(
            {"name": "Test Region 2", "state_id": cls.state_s2.id}
        )
        cls.district_d1 = cls.env["res.district"].create(
            {"name": "Test District 1", "region_id": cls.region_r1.id}
        )
        cls.district_d2 = cls.env["res.district"].create(
            {"name": "Test District 2", "region_id": cls.region_r2.id}
        )

    def test_create_with_district(self):
        partner = self.env["res.partner"].create(
            {"name": "Partner District", "district_id": self.district_d1.id}
        )
        self.assertEqual(partner.district_id, self.district_d1)
        self.assertEqual(partner.region_id, self.region_r1)
        self.assertEqual(partner.state_id, self.state_s1)
        self.assertEqual(partner.country_id, self.country_c1)

    def test_create_with_region(self):
        partner = self.env["res.partner"].create(
            {"name": "Partner Region", "region_id": self.region_r2.id}
        )
        self.assertEqual(partner.region_id, self.region_r2)
        self.assertEqual(partner.state_id, self.state_s2)
        self.assertEqual(partner.country_id, self.country_c1)
        self.assertFalse(partner.district_id)

    def test_create_with_state(self):
        partner = self.env["res.partner"].create(
            {"name": "Partner State", "state_id": self.state_s3.id}
        )
        self.assertEqual(partner.state_id, self.state_s3)
        self.assertEqual(partner.country_id, self.country_c2)
        self.assertFalse(partner.region_id)
        self.assertFalse(partner.district_id)

    def test_write_normalize_territory(self):
        partner = self.env["res.partner"].create({"name": "Partner Write"})
        partner.write({"district_id": self.district_d2.id})
        self.assertEqual(partner.district_id, self.district_d2)
        self.assertEqual(partner.region_id, self.region_r2)
        self.assertEqual(partner.state_id, self.state_s2)
        self.assertEqual(partner.country_id, self.country_c1)

    def test_create_without_territory(self):
        partner = self.env["res.partner"].create({"name": "Partner No Territory"})
        self.assertFalse(partner.district_id)
        self.assertFalse(partner.region_id)
        self.assertFalse(partner.state_id)

    def test_onchange_country_match(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "country_id": self.country_c1.id,
                "state_id": self.state_s1.id,
                "region_id": self.region_r1.id,
                "district_id": self.district_d1.id,
            }
        )
        result = partner._onchange_country_id()
        self.assertTrue(partner.state_id)
        self.assertTrue(partner.region_id)
        self.assertTrue(partner.district_id)
        self.assertEqual(
            result["domain"]["state_id"], [("country_id", "=", self.country_c1.id)]
        )

    def test_onchange_state_match(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "state_id": self.state_s1.id,
                "region_id": self.region_r1.id,
                "district_id": self.district_d1.id,
            }
        )
        result = partner._onchange_state_id()
        self.assertTrue(partner.region_id)
        self.assertTrue(partner.district_id)
        self.assertEqual(
            result["domain"]["region_id"], [("state_id", "=", self.state_s1.id)]
        )

    def test_onchange_region_match(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "region_id": self.region_r1.id,
                "district_id": self.district_d1.id,
            }
        )
        result = partner._onchange_region_id()
        self.assertTrue(partner.district_id)
        self.assertEqual(
            result["domain"]["district_id"], [("region_id", "=", self.region_r1.id)]
        )

    def test_onchange_country_mismatch(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "country_id": self.country_c2.id,
                "state_id": self.state_s1.id,
                "region_id": self.region_r1.id,
                "district_id": self.district_d1.id,
            }
        )
        result = partner._onchange_country_id()
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.region_id)
        self.assertFalse(partner.district_id)
        self.assertEqual(
            result["domain"]["state_id"], [("country_id", "=", self.country_c2.id)]
        )

    def test_onchange_state_mismatch(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "state_id": self.state_s1.id,
                "region_id": self.region_r2.id,
            }
        )
        result = partner._onchange_state_id()
        self.assertFalse(partner.region_id)
        self.assertFalse(partner.district_id)
        self.assertEqual(
            result["domain"]["region_id"], [("state_id", "=", self.state_s1.id)]
        )

    def test_onchange_region_mismatch(self):
        partner = self.env["res.partner"].new(
            {
                "name": "Partner Onchange",
                "region_id": self.region_r1.id,
                "district_id": self.district_d2.id,
            }
        )
        result = partner._onchange_region_id()
        self.assertFalse(partner.district_id)
        self.assertEqual(
            result["domain"]["district_id"], [("region_id", "=", self.region_r1.id)]
        )

    def test_constraint_district_region_mismatch(self):
        partner = self.env["res.partner"].create(
            {"name": "Partner Constraint", "district_id": self.district_d2.id}
        )
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                partner.write({"region_id": self.region_r1.id})

    def test_constraint_region_state_mismatch(self):
        partner = self.env["res.partner"].create(
            {"name": "Partner Constraint", "region_id": self.region_r1.id}
        )
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                partner.write({"state_id": self.state_s3.id})
