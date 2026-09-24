# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentCalibrationPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Calibration Owner"})
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "portal-calibration@test.example.com",
                    "name": "Portal Calibration User",
                    "partner_id": cls.partner.id,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal-calibration",
                }
            )
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {"name": "Calibrated Equipment", "owned_by_id": cls.partner.id}
        )
        cls.certificate = cls.env["fsm.calibration.certificate"].create(
            {
                "name": "CAL-2026-01",
                "fsm_equipment_id": cls.equipment.id,
                "certificate_file": base64.b64encode(b"%PDF-1.4 cal test"),
            }
        )

    def test_page_lists_certificates(self):
        self.authenticate("portal-calibration@test.example.com", "portal-calibration")
        response = self.url_open(f"/my/equipments/{self.equipment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calibration Certificates", response.content)
        self.assertIn(b"CAL-2026-01", response.content)

    def test_portal_user_downloads_certificate(self):
        self.authenticate("portal-calibration@test.example.com", "portal-calibration")
        response = self.url_open(
            f"/my/equipments/calibration/{self.certificate.id}/download"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"%PDF-1.4", response.content)

    def test_anonymous_download_respects_public_setting(self):
        response = self.url_open(
            f"/my/equipments/calibration/{self.certificate.id}/download"
        )
        self.assertNotIn(b"%PDF-1.4", response.content)
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_equipment_portal.public_access", "True"
        )
        response = self.url_open(
            f"/my/equipments/calibration/{self.certificate.id}/download"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"%PDF-1.4", response.content)

    def test_download_missing_certificate_404(self):
        response = self.url_open("/my/equipments/calibration/99999999/download")
        self.assertEqual(response.status_code, 404)
        empty = self.env["fsm.calibration.certificate"].create(
            {"name": "SEM-ARQUIVO", "fsm_equipment_id": self.equipment.id}
        )
        response = self.url_open(f"/my/equipments/calibration/{empty.id}/download")
        self.assertEqual(response.status_code, 404)
