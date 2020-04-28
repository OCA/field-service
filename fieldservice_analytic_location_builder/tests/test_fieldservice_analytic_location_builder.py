# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class FSMAnalyticLocationBuilder(TransactionCase):

    def setUp(self):
        super(FSMAnalyticLocationBuilder, self).setUp()
        self.test_location = self.env.ref('fieldservice.test_location')
        self.test_location.analytic_account_id = self.\
            env['account.analytic.account'].create(
                {
                    'name': 'Test Analytic Account',
                    'partner_id': self.env.ref('fieldservice.'
                                               'test_loc_partner').id
                })
        self.test_loc_partner = self.env.ref('fieldservice.'
                                             'test_loc_partner')
        self.test_location.customer_id = self.test_loc_partner
        self.location_wiz = self.env['fsm.location.builder.wizard'].create({})
        self.location_level_1 = self.env['fsm.location.level'].create(
            {
                'name': 'Floor',
                'spacer': '-',
                'start_number': 0,
                'end_number': 2,
                'wizard_id': self.location_wiz.id
            })
        self.location_level_2 = self.env['fsm.location.level'].create(
            {
                'name': 'Unit',
                'spacer': '',
                'start_number': 0,
                'end_number': 4,
                'wizard_id': self.location_wiz.id
            })

    def test_fsm_location_builder(self):
        # Test createing new sublocations
        before = self.env['fsm.location'].search_count([])
        self.location_wiz.with_context({'active_id': self.test_location.id})\
            .create_sub_locations()
        after = self.env['fsm.location'].search([])
        # Check proper number has been created
        self.assertEqual(before+18, len(after))
        # Ensure their inventory_location_id matches test locaiton inventory
        self.assertEqual(after[-1:].analytic_account_id,
                         self.test_location.analytic_account_id)
