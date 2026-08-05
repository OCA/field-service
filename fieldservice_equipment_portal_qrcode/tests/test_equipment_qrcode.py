# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase


class TestEquipmentQrcode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["fsm.equipment"].create({"name": "QR Equipment"})

    def test_qrcode_url_targets_portal_page(self):
        url = self.equipment._get_qrcode_url()
        self.assertTrue(url.endswith(f"/my/equipments/{self.equipment.id}"))

    def test_qrcode_is_png(self):
        png = base64.b64decode(self.equipment.qrcode)
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_qrcode_empty_for_new_records(self):
        new_equipment = self.env["fsm.equipment"].new({"name": "Virtual"})
        self.assertFalse(new_equipment.qrcode)

    def test_label_report_renders(self):
        html = self.env["ir.actions.report"]._render_qweb_html(
            "fieldservice_equipment_portal_qrcode.action_report_equipment_qr_label",
            self.equipment.ids,
        )[0]
        self.assertIn(b"QR Equipment", html)
        self.assertIn(b"data:image/png;base64", html)
