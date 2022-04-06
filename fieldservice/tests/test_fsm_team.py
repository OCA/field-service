# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, Form


class FSMTeam(TransactionCase):

    def setUp(self):
        super(FSMTeam, self).setUp()
        self.Order = self.env['fsm.order']
        self.Team = self.env['fsm.team']
        self.test_location = self.env.ref('fieldservice.test_location')
        self.test_team = self.Team.create({'name': 'Test Team'})

    def test_fsm_order(self):
        """ Test creating new workorders
            - Active orders
            - Unassigned orders
            - Unscheduled orders
        """
        # Create 5 Orders, which are,
        #   - 2 assigned (3 unassigned)
        #   - 4 scheduled (1 unscheduled)
        todo = {'orders': 5, 'assigned': [3, 4], 'scheduled': [0, 1, 2, 3]}
        view_id = ('fieldservice.fsm_order_form')
        orders = self.Order
        for i in range(todo['orders']):
            with Form(self.Order, view=view_id) as f:
                f.location_id = self.test_location
                f.team_id = self.test_team
            order = f.save()
            orders += order
            order.person_id = i in todo['assigned'] and \
                self.env.ref('fieldservice.person_1') or False
            # TODO: after this https://github.com/OCA/field-service/issues/266
            # assert should then be (5, 3, 1)
            # order.scheduled_date_start = False
        self.assertEqual((self.test_team.order_count,
                          self.test_team.order_need_assign_count,
                          self.test_team.order_need_schedule_count), (5, 3, 0))
