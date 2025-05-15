# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config_model = cls.env["res.config.settings"]

    def test_set_and_get_values(self):
        config = self.config_model.create(
            {
                "max_date_number": "6",
                "max_date_unit": "weeks",
            }
        )

        config.set_values()
        params = self.env["ir.config_parameter"].sudo()
        self.assertEqual(params.get_param("fieldservice.max_date_number"), "6")
        self.assertEqual(params.get_param("fieldservice.max_date_unit"), "weeks")

        values = config.get_values()
        self.assertEqual(values["max_date_number"], "6")
        self.assertEqual(values["max_date_unit"], "weeks")
