# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.addons.fieldservice_account.tests.test_fsm_account import (
    FSMAccountCase
)


class FSMAccountCase(FSMAccountCase):

    def setUp(self):
        super(FSMAccountCase, self).setUp()

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
