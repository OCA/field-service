# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase, Form


class FSMOrder(TransactionCase):

    def setUp(self):
        super(FSMOrder, self).setUp()
        self.Order = self.env['fsm.order']
        self.Agreement = self.env['agreement']
        self.Serviceprofile = self.env['agreement.serviceprofile']
        self.Equipment = self.env['fsm.equipment']
        self.test_location = self.env.ref('fieldservice.test_location')
        self.agreement_type = self.env.ref('agreement_legal.'
                                           'agreement_type_agreement')
        self.test_person = self.env.ref('fieldservice.test_person')

    def test_fsm_agreement(self):
        """
        By create new order and equipment and link to an agreement, I expect,
        - Agreement count and link to the order/equipment is corrrect
        - Location's service profile display correctly
        - Person (partner) can relate back to agreement correctly
        """
        # Create agreement and assign to test location
        view_id = ('agreement_legal.partner_agreement_form_view')
        with Form(self.Agreement, view=view_id) as f:
            f.name = 'Test Agreement'
            f.agreement_type_id = self.agreement_type
            f.description = 'Test Agreement'
            f.start_date = f.end_date = fields.Date.today()
            f.fsm_location_id = self.test_location
            f.partner_id = self.test_person.partner_id
        agreement = f.save()
        profile = self.Serviceprofile.create({'name': 'Test Profile',
                                              'agreement_id': agreement.id})
        # Create 2 Orders, that link to this agreement
        view_id = ('fieldservice.fsm_order_form')
        with Form(self.Order, view=view_id) as f:
            f.location_id = self.test_location
            f.agreement_id = agreement
        order1 = f.save()
        order2 = order1.copy()
        self.assertEqual(agreement.service_order_count, 2)
        self.assertEqual([order1.id, order2.id],
                         agreement.action_view_service_order()['domain'][0][2])
        # Create 3 equipment, that link to this agreement
        view_id = ('fieldservice.fsm_equipment_form_view')
        with Form(self.Equipment, view=view_id) as f:
            f.name = 'EQ1'
            f.current_location_id = self.test_location
            f.agreement_id = agreement
        equipment1 = f.save()
        equipment2 = equipment1.copy({'name': 'EQ2'})
        equipment3 = equipment1.copy({'name': 'EQ3'})
        self.assertEqual(agreement.equipment_count, 3)
        self.assertEqual([equipment1.id, equipment2.id, equipment3.id],
                         agreement.action_view_fsm_equipment()['domain'][0][2])
        # Location's service profile display correctly
        self.assertEqual(self.test_location.serviceprofile_ids, profile)
        # Person (partner) can relate back to agreement correctly
        self.assertEqual(self.test_person.agreement_count, 1)
        self.assertEqual(self.test_person.action_view_agreements()['res_id'],
                         agreement.id)
