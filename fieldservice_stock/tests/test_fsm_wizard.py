# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class FSMWizard(TransactionCase):
    """
    Test used to check that the base functionalities of Field Service Stock.
    """

    def setUp(cls):
        super().setUp()
        cls.Wizard = cls.env["fsm.wizard"]
        cls.test_inventory_location = cls.env.ref(
            "fieldservice_stock.stock_location_field"
        )
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "phone": "1234567890",
                "email": "tp@email.com",
                "property_stock_customer": cls.test_inventory_location.id,
            }
        )

    def test_prepare_location(self):
        res = self.Wizard._prepare_fsm_location(self.test_partner)

        self.assertEqual(res["inventory_location_id"], self.test_inventory_location.id)
