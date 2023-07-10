# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, new_test_user

from odoo.addons.fieldservice_fleet import hooks


class TestFSMFleetWizard(TransactionCase):
    def setUp(self):
        super(TestFSMFleetWizard, self).setUp()
        self.Wizard = self.env["fsm.fleet.wizard"]
        self.fleet_vehicle_1 = self.env.ref("fleet.vehicle_1")
        self.person_1 = self.env.ref("fieldservice.person_1")
        self.driver_1 = self.env.ref("base.res_partner_address_25")

    def test_convert_vehicle(self):
        # Convert a Fleet vehicle to FSM vehicle and link it
        self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)

        # Search FSM vehicle records linked to the test Fleet vehicle
        fsm_vehicle = self.env["fsm.vehicle"].search(
            [("fleet_vehicle_id", "=", self.fleet_vehicle_1.id)]
        )

        # Create a driver partner without an associated fsm.person record
        driver_partner = self.env["res.partner"].create(
            {
                "name": "Driver Partner",
            }
        )

        # Retrieve the fsm_worker record for the driver partner
        fsm_worker = self.env["fsm.person"].search(
            [("partner_id", "=", driver_partner.id)]
        )

        self.assertEqual(
            len(fsm_vehicle),
            1,
            """FSM Fleet Wizard: Did not find FSM vehicle
               linked to Fleet vehicle""",
        )
        self.assertEqual(
            fsm_vehicle.name,
            self.fleet_vehicle_1.name,
            """FSM Fleet Wizard: FSM Vehicle and Fleet Vehicle
               names do not match""",
        )
        self.assertTrue(
            self.fleet_vehicle_1.is_fsm_vehicle,
            """FSM Fleet Wizard: Fleet vehicle boolean field
               is_fsm_vehicle is False""",
        )
        self.assertEqual(
            fsm_vehicle.person_id.partner_id,
            self.fleet_vehicle_1.driver_id,
            """FSM Fleet Wizard: FSM vehicle driver is not same
               as the Fleet vehicle driver""",
        )
        self.assertTrue(
            self.fleet_vehicle_1.driver_id and self.fleet_vehicle_1.is_fsm_vehicle,
            "Driver ID and is_fsm_vehicle condition is not True",
        )

        # Set the driver_id of the fleet vehicle to the driver partner
        self.fleet_vehicle_1.driver_id = driver_partner.id

        # Assert that fsm_worker is not found
        self.assertFalse(
            fsm_worker, "FSM worker found for driver partner, but it should not exist"
        )

        # Attempt to convert the Fleet vehicle again, but expect UserError
        # because we already converted it
        with self.assertRaises(UserError):
            self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)

    def test_fsm_vehicle(self):
        self.fleet_vehicle_2 = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 2",
                "person_id": self.person_1.id,
                "fleet_vehicle_id": self.fleet_vehicle_1.id,
            }
        )
        self.fleet_vehicle_1.is_fsm_vehicle = True
        self.fleet_vehicle_2.write({"driver_id": self.driver_1.id})
        manager = new_test_user(
            self.env,
            "test fleet manager",
            groups="fleet.fleet_group_manager,base.group_partner_manager",
        )
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        model = self.env["fleet.vehicle.model"].create(
            {
                "brand_id": brand.id,
                "name": "A3",
            }
        )
        hooks.pre_init_hook(self.env.cr)
        self.fleet_vehicle_3 = (
            self.env["fleet.vehicle"]
            .with_user(manager)
            .create(
                {
                    "model_id": model.id,
                    "driver_id": user.partner_id.id,
                    "plan_to_change_car": False,
                }
            )
        )
        self.context = {
            "active_model": "fleet.vehicle",
            "active_ids": [self.fleet_vehicle_3.id],
            "active_id": self.fleet_vehicle_3.id,
        }
        self.Wizard.with_context(**self.context).action_convert()
