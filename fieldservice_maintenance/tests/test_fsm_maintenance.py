# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMMaintenance(TransactionCase):
    def test_fsm_maintenance(self):
        # Create FSM Location to use in test cases
        partner = self.env["res.partner"].create(
            {
                "name": "Partner",
            }
        )
        fsm_loc = self.env["fsm.location"].create(
            {"name": "Test Maintenance Location", "owner_id": partner.id}
        )
        # Create FSM equipment
        fsm_equip_01 = self.env["fsm.equipment"].create(
            {
                "name": "Test FSM Equipment 01",
                "current_location_id": fsm_loc.id,
            }
        )
        maint_equip_01 = fsm_equip_01.maintenance_equipment_id
        self.assertTrue(maint_equip_01)
        # Create FSM Order of type maintenance and an equipment. This should
        # create a maintenance request based on the FSM order
        fsm_order_01 = self.env["fsm.order"].create(
            {
                "location_id": fsm_loc.id,
                "type": self.env.ref(
                    "fieldservice_maintenance.fsm_order_type_maintenance"
                ).id,
                "equipment_id": fsm_equip_01.id,
            }
        )
        # Verify Maintenance order was created for that equipment
        maint_req_01 = self.env["maintenance.request"].search(
            [("fsm_order_id", "=", fsm_order_01.id)]
        )
        self.assertEqual(maint_req_01.name, fsm_order_01.name)
        self.assertEqual(
            maint_req_01.equipment_id,
            fsm_order_01.equipment_id.maintenance_equipment_id,
        )
        self.assertEqual(fsm_order_01.request_id, maint_req_01)

        # Create a maintenance request for an FSM equipment. This should
        # create FSM order for that equipment.
        maint_req_02 = self.env["maintenance.request"].create(
            {
                "name": "Equip 01 Request for FSM",
                "equipment_id": maint_equip_01.id,
            }
        )
        # Test order was created for the request
        fsm_order_02 = self.env["fsm.order"].search(
            [("request_id", "=", maint_req_02.id)]
        )
        self.assertEqual(fsm_order_02.description, maint_req_02.description)
        self.assertEqual(
            fsm_order_02.equipment_id.maintenance_equipment_id,
            maint_req_02.equipment_id,
        )
        self.assertEqual(maint_req_02.fsm_order_id, fsm_order_02)

        # Create a maintenance request when fsm_equipment's location is not set
        fsm_equip_01.current_location_id = False
        request = self.env["maintenance.request"].create(
            {
                "name": "Equip 01 Request",
                "equipment_id": maint_equip_01.id,
            }
        )
        # and check that a notification regarding its missing value
        # is shown to the user
        msg_notification = self.env["mail.message"].search(
            [("res_id", "=", request.id)], order="id desc", limit=1
        )
        self.assertRegex(
            msg_notification.body,
            r".*Order was not created because the equipment's location is not set.*",
        )

        # Deleting the FSM Equipment
        fsm_equip_01.unlink()
        # Verfiy the maintenance equipment is no longer a FSM equipment
        self.assertFalse(maint_equip_01.is_fsm_equipment)
