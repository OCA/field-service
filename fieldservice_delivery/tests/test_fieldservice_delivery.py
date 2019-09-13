# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase, Form


class TestFieldServiceDelivery(TransactionCase):

    def setUp(self):
        super(TestFieldServiceDelivery, self).setUp()
        self.FSMorder = self.env['fsm.order']
        # Create Order
        self.test_owner = self.env.ref('base.res_partner_12')
        self.test_customer = self.env.ref('base.res_partner_10')
        self.test_category = self.env.ref('base.res_partner_category_0')
        self.test_product = self.env.ref('product.product_product_1')
        # Create Inventory Location
        self.test_location = self.env['stock.location'].create({
            'name': 'TEST LOCATION',
        })
        # Create Location
        self.test_location_id = self.env['fsm.location'].create({
            'name': 'TEST',
            'owner_id': self.test_owner.id,
            'customer_id': self.test_customer.id,
            'category_id': self.test_category,
            'inventory_location_id': self.test_location.id,
        })
        # Create Delivery Carrier
        self.test_carrier_id = self.env['delivery.carrier'].create({
            'name': 'TEST Free Delivery ',
            'free_over': True,
            'product_id': self.test_product.id
        })

    def test_fieldservice_delivery(self):
        """Create order and follow USAGE"""
        with Form(self.FSMorder) as f:
            f.location_id = self.test_location_id
            f.priority = '1'
            f.carrier_id = self.test_carrier_id
            with f.stock_request_ids.new() as line:
                line.product_id = self.test_product
                line.direction = 'outbound'
                line.product_uom_qty = 11
        order = f.save()
        order.action_request_submit()
