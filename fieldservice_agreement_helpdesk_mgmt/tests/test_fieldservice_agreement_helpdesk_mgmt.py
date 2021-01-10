# Copyright (C) 2020 - TODAY, Marcel Savegnago (Escodoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestFieldserviceAgreementHelpdeskMgmt(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFieldserviceAgreementHelpdeskMgmt, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@test.com',
        })

        cls.location = cls.env['fsm.location'].create({
            'name': 'Test Location',
            'partner_id': cls.partner.id,
            'owner_id': cls.partner.id,
            'customer_id': cls.partner.id,
        })

        cls.agreement = cls.env['agreement'].create({
            'name': 'Test Agreement',
            'partner_id': cls.partner.id,
            'fsm_location_id': cls.location.id,
        })

        cls.ticket = cls.env['helpdesk.ticket'].create({
            'name': 'Test Helpdesk Ticket',
            'description': 'Test Helpdesk Ticket',
            'fsm_location_id': cls.location.id,
            'agreement_id': cls.agreement.id,
        })

    def test_create_fsm_order(self):
        action_create_order = self.ticket.action_create_order()

        self.assertEqual(
            action_create_order["context"]["default_agreement_id"],
            self.agreement.id
        )
