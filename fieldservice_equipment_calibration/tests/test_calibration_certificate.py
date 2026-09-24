# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
