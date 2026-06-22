# Copyright (C) 2020 - TODAY, Marcel Savegnago (Escodoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestFSMEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Equipment = cls.env["fsm.equipment"]
        cls.stock_location = cls.env.ref("stock.stock_location_customers")
        cls.current_location = cls.env.ref("fieldservice.location_1")
        cls.test_location = cls.env.ref("fieldservice.test_location")

        currency = cls.env["res.currency"].create(
            {
                "name": "Currency 1",
                "symbol": "$",
            }
        )
        partner = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        cls.company1 = cls.env["res.company"].create(
            {
                "name": "Company 1",
                "currency_id": currency.id,
                "partner_id": partner.id,
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "tracking": "serial",
            }
        )
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "serial1",
                "product_id": cls.product1.id,
                "company_id": cls.company1.id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product1.id,
                "location_id": cls.stock_location.id,
                "quantity": 1.0,
                "lot_id": cls.lot1.id,
            }
        )

        cls.equipment = cls.Equipment.create(
            {
                "name": "Equipment 1",
                "product_id": cls.product1.id,
                "lot_id": cls.lot1.id,
                "current_stock_location_id": cls.stock_location.id,
            }
        )

    def test_onchange_product(self):
        equipment = self.equipment
        equipment._onchange_product()
        self.assertFalse(equipment.current_stock_location_id)

    def test_compute_current_stock_loc_id(self):
        equipment = self.equipment
        equipment._compute_current_stock_loc_id()
        self.assertTrue(equipment.current_stock_location_id == self.stock_location)

    def test_fsm_equipment(self):
        # Create an equipment
        view_id = "fieldservice.fsm_equipment_form_view"
        with Form(self.Equipment, view=view_id) as f:
            f.name = "Test Equipment 1"
            f.current_location_id = self.current_location
            f.location_id = self.test_location
            f.lot_id = self.lot1
            f.product_id = self.product1
        equipment = f.save()

        self.assertEqual(f.id, equipment.lot_id.fsm_equipment_id.id)
