# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFSMEquipmentWarranty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ProductTemplate = cls.env["product.template"]

        tmpl_month = ProductTemplate.create(
            {"name": "Product 3M", "warranty": 3, "warranty_type": "month"}
        )
        cls.product_month = tmpl_month.product_variant_id

        cls.Equipment = cls.env["fsm.equipment"]
        cls.start_a = fields.Date.to_date("2025-01-15")
        cls.start_b = fields.Date.to_date("2025-02-10")

    def test_01_create_sets_warranty_end_date(self):
        equip = self.Equipment.create(
            {
                "name": "Equip A",
                "product_id": self.product_month.id,
                "warranty_start_date": self.start_a,
            }
        )
        expected = self.start_a + relativedelta(months=3)
        self.assertEqual(equip.warranty_end_date, expected)

    def test_02_write_recomputes_on_start_date_change(self):
        equip = self.Equipment.create(
            {
                "name": "Equip B",
                "product_id": self.product_month.id,
                "warranty_start_date": self.start_a,
            }
        )
        equip.write({"warranty_start_date": self.start_b})
        expected = self.start_b + relativedelta(months=3)
        self.assertEqual(equip.warranty_end_date, expected)

    def test_03_create_without_product_sets_today(self):
        today = fields.Date.today()
        equip = self.Equipment.create(
            {
                "name": "Equipment without product",
                "warranty_start_date": self.start_a,
            }
        )
        self.assertEqual(equip.warranty_end_date, today)
