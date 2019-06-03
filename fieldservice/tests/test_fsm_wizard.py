# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class FieldServiceTransactionCase(TransactionCase):
    """
        Test used to check that the base functionalities of Field Service.
        - test_convert_location: tests that a res.partner can be converted
        into a fsm.location.
        - test_convert_person: tests that a res.partner can be converted into
        a fsm.person.
        - test_convert_sublocation: tests that the sub-contacts on a
        res.partner are converted into Other Addresses.
    """
    def setUp(self):
        super(FieldServiceTransactionCase, self).setUp()
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
        # create expected FSM Person to compare to converted FSM Person
        self.test_person = self.env['fsm.person'].\
            create({
                'name': 'Test Person',
                'phone': '123',
                'email': 'tp@email.com',
                })
        self.test_wizard = self.env['fsm.wizard']

    def test_convert_location(self):
        # convert test_partner to FSM Location
        self.test_wizard.action_convert_location(self.test_partner)

        # check if there is a new FSM Location with name 'Test Partner'
        self.wiz_location = self.env['fsm.location'].\
            search([('name', '=', 'Test Partner')])

        # check if 'Test Partner' creation successful and fields copied over
        self.assertEqual(self.test_location.phone, self.wiz_location.phone)
        self.assertEqual(self.test_location.email, self.wiz_location.email)

    def test_convert_person(self):
        # convert test_partner to FSM Person
        self.test_wizard.action_convert_person(self.test_partner)

        # check if there is a new FSM Person with name 'Test Partner'
        self.wiz_person = self.env['fsm.person'].\
            search([('name', '=', 'Test Partner')])

        # check if 'Test Partner' creation successful and fields copied over
        self.assertEqual(self.test_person.phone, self.wiz_person.phone)
        self.assertEqual(self.test_person.email, self.wiz_person.email)

    def test_convert_sublocation(self):
        # create 4 Res Partners each with different type
        s1 = self.env['res.partner'].create({
            'name': 'sub partner 1',
            'type': 'contact'
        })
        s2 = self.env['res.partner'].create({
            'name': 'sub partner 2',
            'type': 'invoice'
        })
        s3 = self.env['res.partner'].create({
            'name': 'sub partner 3',
            'type': 'delivery'
        })
        s4 = self.env['res.partner'].create({
            'name': 'sub partner 4',
            'type': 'private'
        })

        # create parent Res Partner and assign its children
        children = [s1.id, s2.id, s3.id, s4.id]
        parent = s1 = self.env['res.partner'].create({
            'name': 'Parent Partner',
            'child_ids': [(6, 0, children)]
        })

        # convert Parent Partner to FSM Location
        self.test_wizard.action_convert_location(parent)

        # check if 'Parent Partner' creation successful and fields copied over
        wiz_parent = self.env['fsm.location'].\
            search([('name', '=', 'Parent Partner')])

        # check all children were assigned type 'other'
        for child in wiz_parent.child_ids:
            self.assertEqual(child.type, 'other')
