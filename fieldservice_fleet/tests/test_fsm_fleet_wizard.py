
# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestFSMFleetWizard(TransactionCase):

    def setUp(self):
        super(TestFSMFleetWizard, self).setUp()
        self.Wizard = self.env['fsm.fleet.wizard']
        self.fleet_vehicle_1 = self.env.ref('fleet.vehicle_1')

    def test_convert_vehicle(self):
        # Convert a Fleet vehicle to FSM vehicle and link it
        self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)

        # Search FSM vehicle records linked to the test Fleet vehicle
        fsm_vehicle = self.env['fsm.vehicle'].search([
            ('fleet_vehicle_id', '=', self.fleet_vehicle_1.id)
        ])

        self.assertEqual(
            len(fsm_vehicle), 1,
            """FSM Fleet Wizard: Did not find FSM vehicle
               linked to Fleet vehicle"""
        )
        self.assertEqual(
            fsm_vehicle.name, self.fleet_vehicle_1.name,
            """FSM Fleet Wizard: FSM Vehicle and Fleet Vehicle
               names do not match"""
        )
        self.assertTrue(
            self.fleet_vehicle_1.is_fsm_vehicle,
            """FSM Fleet Wizard: Fleet vehicle boolean field
               is_fsm_vehicle is False"""
        )
        self.assertEqual(
            fsm_vehicle.person_id.partner_id,
            self.fleet_vehicle_1.driver_id,
            """FSM Fleet Wizard: FSM vehicle driver is not same
               as the Fleet vehicle driver"""
        )

        # Attempt to convert the Fleet vehicle again, but expect UserError
        # because we already converted it
        with self.assertRaises(UserError) as e:
            self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)
        self.assertEqual(
            e.exception.name,
            'A Field Service Vehicle related to that'
            ' Fleet Vehicle already exists.',
            """FSM Fleet Wizard: UserError not thrown when converting
               Fleet vehicle already linked to FSM Vehicle."""
        )
