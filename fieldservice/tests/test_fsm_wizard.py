# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class FSMWizard(TransactionCase):
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
        super(FSMWizard, self).setUp()
        self.Wizard = self.env["fsm.wizard"]
        self.test_partner = self.env.ref("fieldservice.test_partner")
        self.test_parent_partner = self.env.ref("fieldservice.test_parent_partner")
        self.test_loc_partner = self.env.ref("fieldservice.test_loc_partner")
        self.test_location = self.env.ref("fieldservice.test_location")
        self.test_person = self.env.ref("fieldservice.test_person")

    def test_convert_location(self):
        # convert test_partner to FSM Location
        self.Wizard.action_convert_location(self.test_partner)

        # check if there is a new FSM Location with name 'Test Partner'
        self.wiz_location = self.env["fsm.location"].search(
            [("name", "=", "Test Partner")]
        )

        # check if 'Test Partner' creation successful and fields copied over
        self.assertEqual(self.test_location.phone, self.wiz_location.phone)
        self.assertEqual(self.test_location.email, self.wiz_location.email)

    def test_convert_person(self):
        # convert test_partner to FSM Person
        self.Wizard.action_convert_person(self.test_partner)

        # check if there is a new FSM Person with name 'Test Partner'
        self.wiz_person = self.env["fsm.person"].search([("name", "=", "Test Partner")])

        # check if 'Test Partner' creation successful and fields copied over
        self.assertEqual(self.test_person.phone, self.wiz_person.phone)
        self.assertEqual(self.test_person.email, self.wiz_person.email)

    def test_convert_sublocation(self):
        # convert Parent Partner to FSM Location
        self.Wizard.action_convert_location(self.test_parent_partner)

        # check if 'Parent Partner' creation successful and fields copied over
        wiz_parent = self.env["fsm.location"].search([("name", "=", "Parent Partner")])

        # check all children were assigned type 'other'
        for child in wiz_parent.child_ids:
            self.assertEqual(child.type, "other")
