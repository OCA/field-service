# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from datetime import datetime
from odoo.tests import TransactionCase


class TestFieldserviceRouteStock(TransactionCase):

    def setUp(self):
        super(TestFieldserviceRouteStock, self).setUp()
        self.day_route_obj = self.env['fsm.route.dayroute']
        self.worker = self.env.ref('fieldservice.person_1')
        self.vehicle_obj = self.env['fsm.vehicle']
        self.location = self.env.ref('stock.stock_location_stock')
        self.inventory_obj = self.env['stock.inventory']
        self.stage_obj = self.env['fsm.stage']
        self.account_obj = self.env['account.account']
        rec_user_type_id = self.env.ref('account.data_account_type_receivable')
        pay_user_type_id = self.env.ref('account.data_account_type_payable')
        bank_user_type_id = self.env.ref('account.data_account_type_liquidity')

        self.receivable_account_id = self.account_obj.create(
            {'name': 'Test Receivable',
             'code': '10000',
             'user_type_id': rec_user_type_id.id,
             'reconcile': True})
        self.payable_account_id = self.account_obj.create(
            {'name': 'Test Payable',
             'code': '20000',
             'user_type_id': pay_user_type_id.id,
             'reconcile': True})
        self.stock_input_account_id = self.account_obj.create({
            'name': 'Test Stock Input',
            'code': '10001',
            'user_type_id': bank_user_type_id.id,
            'reconcile': True
        })
        self.stock_output_account_id = self.account_obj.create({
            'name': 'Test Stock Output',
            'code': '10002',
            'user_type_id': bank_user_type_id.id,
            'reconcile': True
        })
        self.stock_valuation_account_id = self.account_obj.create({
            'name': 'Test Stock Valuation',
            'code': '10003',
            'user_type_id': bank_user_type_id.id,
            'reconcile': True
        })
        self.categ_id = self.env.ref('product.product_category_all')
        self.categ_id.property_valuation = 'real_time'
        self.categ_id.property_stock_account_input_categ_id = \
            self.stock_input_account_id.id
        self.categ_id.property_stock_account_output_categ_id = \
            self.stock_output_account_id.id
        self.categ_id.property_stock_valuation_account_id = \
            self.stock_valuation_account_id.id

        self.worker.property_account_receivable_id = \
            self.receivable_account_id.id
        self.worker.property_account_payable_id = self.payable_account_id.id
        self.default_stage = self.env.ref(
            'fieldservice_route.fsm_stage_route_new')
        self.closed_stage = self.env.ref(
            'fieldservice_route.fsm_stage_route_close')
        self.model_id = self.env.ref('fleet.model_corsa')

    def test_check_stock_inventory(self):
        self.vehicle = self.vehicle_obj.create({
            'name': 'Test Vehicle',
            'person_id': self.worker.id,
            'inventory_location_id': self.location.id,
            'model_id': self.model_id.id,
        })

        route_vals = {
            'name': 'Test Day Route',
            'person_id': self.worker.id,
            'fsm_vehicle_id': self.vehicle.id,
            'date': datetime.now().date(),
        }

        route_id = self.day_route_obj.create(route_vals)

        inventory_id = self.inventory_obj.search([('filter', '=', 'none'),
                                                  ('state', '=', 'draft'), ],
                                                 limit=1)
        if not inventory_id:
            inventory_id = self.inventory_obj.with_context(
                dayroute_id=route_id.id).create({'name': "Test Inventory", })

        route_id.final_inventory_id = inventory_id.id
        route = self.day_route_obj.search_count([])
        inventory = self.inventory_obj.search_count([])
        self.assertTrue(route >= 1)
        self.assertTrue(inventory >= 1)
        inventory_id.action_start()
        for line in inventory_id.line_ids:
            if line.theoretical_qty < 0:
                line.theoretical_qty = 1
            line.product_qty = line.theoretical_qty + 5

        inventory_id.action_validate()
        route_id.stage_id = self.closed_stage.id
        self.assertTrue(inventory_id.adjustment_move_id.id)
