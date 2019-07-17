from odoo.tests.common import TransactionCase, Form


class TestFieldServiceStock(TransactionCase):

    def setUp(self):
        super(TestFieldServiceStock, self).setUp()
        self.ServiceLocation = self.env['fsm.location']
        self.Order = self.env['fsm.order']

        self.test_product = self.env.ref('product.product_product_11')
        self.uom_unit_id = self.ref('uom.product_uom_unit')
        # Create Inventory Location
        self.test_location = self.env['stock.location'].create({
            'name': 'TEST LOCATION',
        })
        # Create Service Location
        self.test_location_id = self.env['fsm.location'].create({
            'name': 'TEST',
            'owner_id': self.test_owner.id,
            'customer_id': self.test_customer.id,
            'category_id': self.test_category,
            'inventory_location_id': self.test_location.id,
        })

    def test_create_order(self):
        with Form(self.Order) as f:
            f.location_id = self.test_location_id
            with f.stock_request_ids.new() as line:
                line.product_id = self.test_product
                line.product_uom_id = self.uom_unit_id
                line.direction = 'outbound'
                line.product_uom_qty = 1
