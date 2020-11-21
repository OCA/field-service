# Copyright (C) 2020 - TODAY, Marcel Savegnago (Escodoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestFSMEquipment(TransactionCase):

    def setUp(self):
        super(TestFSMEquipment, self).setUp()
        self.Equipment = self.env['fsm.equipment']
        self.stock_location = self.env.ref('stock.stock_location_customers')

        product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
        })
        lot1 = self.env['stock.production.lot'].create({
            'name': 'serial1',
            'product_id': product1.id,
        })
        self.env['stock.quant'].create({
            'product_id': product1.id,
            'location_id': self.stock_location.id,
            'quantity': 1.0,
            'lot_id': lot1.id,
        })

        self.equipment = self.Equipment.create({
            'name': 'Equipment 1',
            'product_id': product1.id,
            'lot_id': lot1.id,
            'current_stock_location_id': self.stock_location.id,
        })

    def test_onchange_product(self):
        equipment = self.equipment
        equipment._onchange_product()
        self.assertFalse(equipment.current_stock_location_id)

    def test_compute_current_stock_loc_id(self):
        equipment = self.equipment
        equipment._compute_current_stock_loc_id()
        self.assertTrue(equipment.current_stock_location_id == self.stock_location)
