# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class FSMAccountCase(TransactionCase):

    def setUp(self):
        super(FSMAccountCase, self).setUp()
        self.Wizard = self.env['fsm.wizard']
        self.WorkOrder = self.env['fsm.order']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']
        # create a Res Partner
        self.test_partner = self.env['res.partner'].\
            create({
                'name': 'Test Partner',
                'phone': '123',
                'email': 'tp@email.com',
                })
        # create a Res Partner to be converted to FSM Location/Person
        self.test_loc_partner = self.env['res.partner'].\
            create({
                'name': 'Test Loc Partner',
                'phone': 'ABC',
                'email': 'tlp@email.com',
                })
        self.test_loc_partner2 = self.env['res.partner'].\
            create({
                'name': 'Test Loc Partner 2',
                'phone': '123',
                'email': 'tlp@example.com',
                })
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env['fsm.location'].\
            create({
                'name': 'Test Location',
                'phone': '123',
                'email': 'tp@email.com',
                'partner_id': self.test_loc_partner.id,
                'owner_id': self.test_loc_partner.id,
                'customer_id': self.test_loc_partner.id,
                })

    def test_convert_contact_to_fsm_location(self):
        """
        Test converting a contact to a location to make sure the customer_id
        and owner_id get set correctly
        :return:
        """
        self.Wizard.action_convert_location(self.test_loc_partner2)

        # check if there is a new FSM Location with the same name
        self.wiz_location = self.env['fsm.location']. \
            search([('name', '=', self.test_loc_partner2.name)])

        # check if location is created successfully and fields copied over
        self.assertEqual(self.test_loc_partner2,
                         self.wiz_location.customer_id)
        self.assertEqual(self.test_loc_partner2,
                         self.wiz_location.owner_id)
