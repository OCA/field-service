from odoo.tests.common import TransactionCase, Form


class TestFieldServiceDelivery(TransactionCase):

    def setUp(self):
        super(TestFieldServiceDelivery, self).setUp()
        self.FSMorder = self.env['fsm.order']

        # Create Order
        self.test_owner = self.env.ref('base.res_partner_12')
        self.test_customer = self.env.ref('base.res_partner_10')
        self.test_category = self.env.ref('base.res_partner_category_0')
        self.test_product = self.env.ref('product.product_product_8')
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

    def test_priority_1_fieldservice_delivery(self):
        """Create order and follow USAGE"""
        with Form(self.FSMorder) as f:
            f.location_id = self.test_location_id
            f.priority = '1'
            with f.stock_request_ids.new() as line:
                line.product_id = self.test_product
                line.direction = 'inbound'
                line.product_uom_qty = 1
        f.save()

    def test_priority_2_fieldservice_delivery(self):
        """Create order and follow USAGE"""
        with Form(self.FSMorder) as f:
            f.location_id = self.test_location_id
            f.priority = '2'
            with f.stock_request_ids.new() as line:
                line.product_id = self.test_product
                line.direction = 'inbound'
                line.product_uom_qty = 1
        f.save()

    def test_priority_3_fieldservice_delivery(self):
        """Create order and follow USAGE"""
        with Form(self.FSMorder) as f:
            f.location_id = self.test_location_id
            f.priority = '3'
            with f.stock_request_ids.new() as line:
                line.product_id = self.test_product
                line.direction = 'inbound'
                line.product_uom_qty = 1
        f.save()
