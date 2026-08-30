# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentSerialRoute(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Serial Device",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "SER-0099", "product_id": cls.product.id}
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "Serial Equipment",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
            }
        )

    def test_serial_route_redirects_to_equipment_page(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_equipment_portal.public_access", "True"
        )
        response = self.url_open("/my/equipments/serial/SER-0099")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.url.endswith(f"/my/equipments/{self.equipment.id}"))
        self.assertIn(b"Serial Equipment", response.content)

    def test_serial_route_unknown_serial_404(self):
        response = self.url_open("/my/equipments/serial/NAO-EXISTE")
        self.assertEqual(response.status_code, 404)
