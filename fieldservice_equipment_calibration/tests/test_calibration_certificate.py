# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestCalibrationCertificate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["fsm.equipment"].create(
            {"name": "Test Calibrated Equipment"}
        )

    def test_certificate_lifecycle(self):
        certificate = self.env["fsm.calibration.certificate"].create(
            {
                "name": "CAL-2026-001",
                "initial_date": "2026-01-01",
                "expiration_date": "2027-01-01",
                "fsm_equipment_id": self.equipment.id,
            }
        )
        self.assertTrue(certificate.active)
        self.assertEqual(self.equipment.fsm_calibration_certificate_ids, certificate)

    def test_archived_certificate_leaves_active_list(self):
        certificate = self.env["fsm.calibration.certificate"].create(
            {
                "name": "CAL-2026-002",
                "fsm_equipment_id": self.equipment.id,
            }
        )
        certificate.active = False
        self.assertNotIn(certificate, self.equipment.fsm_calibration_certificate_ids)
        self.assertIn(
            certificate,
            self.env["fsm.calibration.certificate"]
            .with_context(active_test=False)
            .search([("fsm_equipment_id", "=", self.equipment.id)]),
        )


class TestCalibrationCertificateMultiCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Certificate = cls.env["fsm.calibration.certificate"]
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Calibration Co B"})
        cls.equipment_b = (
            cls.env["fsm.equipment"]
            .with_company(cls.company_b)
            .create({"name": "Equipment B", "company_id": cls.company_b.id})
        )
        cls.user_a = new_test_user(
            cls.env,
            login="calibration_user_a",
            groups="fieldservice.group_fsm_manager",
            company_id=cls.company_a.id,
            company_ids=[(6, 0, cls.company_a.ids)],
        )

    def test_company_follows_equipment(self):
        certificate = self.Certificate.create(
            {"name": "CAL-B-001", "fsm_equipment_id": self.equipment_b.id}
        )
        self.assertEqual(certificate.company_id, self.company_b)

    def test_company_defaults_without_equipment(self):
        certificate = self.Certificate.create({"name": "CAL-NO-EQ"})
        self.assertEqual(certificate.company_id, self.company_a)
        certificate.company_id = self.company_b
        certificate.fsm_equipment_id = False
        self.assertEqual(certificate.company_id, self.company_b)

    def test_equipment_company_must_match(self):
        certificate = self.Certificate.create(
            {"name": "CAL-B-002", "fsm_equipment_id": self.equipment_b.id}
        )
        with self.assertRaises(UserError):
            certificate.company_id = self.company_a

    def test_certificate_not_readable_across_companies(self):
        certificate = self.Certificate.create(
            {"name": "CAL-B-003", "fsm_equipment_id": self.equipment_b.id}
        )
        as_user_a = self.Certificate.with_user(self.user_a)
        self.assertFalse(as_user_a.search([("id", "=", certificate.id)]))
        with self.assertRaises(AccessError):
            as_user_a.browse(certificate.id).read(["name"])
