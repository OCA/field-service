# Copyright (C) 2022, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestFSMVehicleStock(TransactionCase):
    def setUp(self):
        super(TestFSMVehicleStock, self).setUp()

        # Set up inventory locations
        self.veh_parent_loc = self.env.ref(
            "fieldservice_vehicle_stock.stock_location_vehicle_storage"
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.veh_1_loc = self.env["stock.location"].create(
            {
                "name": "Vehicle 1 Storage",
                "location_id": self.veh_parent_loc.id,
                "usage": "internal",
            }
        )
        self.veh_2_loc = self.env["stock.location"].create(
            {
                "name": "Vehicle 2 Storage",
                "location_id": self.veh_parent_loc.id,
                "usage": "internal",
            }
        )
        self.non_vehicle_stock_loc = self.env["stock.location"].create(
            {
                "name": "Other Stock Location",
                "location_id": self.stock_location.id,
                "usage": "internal",
            }
        )

        # Set up FSM Vehicles with inventory locations
        self.fsm_veh_1 = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 1",
                "inventory_location_id": self.veh_1_loc.id,
            }
        )
        self.fsm_veh_2 = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 2",
                "inventory_location_id": self.veh_2_loc.id,
            }
        )
        self.fsm_veh_bad_loc = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle with Incorrect Location",
                "inventory_location_id": self.non_vehicle_stock_loc.id,
            }
        )

        # Set up product and stock it to use for a transfer
        self.product = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 100
        )

        # Set up a transfer using the operation type for vehicle loading
        self.picking_type_id = self.env.ref(
            "fieldservice_vehicle_stock.picking_type_output_to_vehicle"
        )
        self.picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.veh_parent_loc.id,
            }
        )
        self.move = self.env["stock.move"].create(
            {
                "name": "Test Vehicle Stock Move",
                "location_id": self.stock_location.id,
                "location_dest_id": self.veh_parent_loc.id,
                "product_id": self.product.id,
                "product_uom_qty": 8.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "picking_id": self.picking_out.id,
            }
        )

        # Setup FSM Order
        self.fsm_location = self.env.ref("fieldservice.test_location")
        self.fsm_order_1 = self.env["fsm.order"].create(
            {
                "name": "FSM Order 1",
                "location_id": self.fsm_location.id,
            }
        )

    def test_fsm_vehicle_stock(self):
        self.picking_out.action_assign()
        # Test confirm transfer w/out a vehicle
        with self.assertRaises(UserError):
            self.picking_out._action_done()
        # Write FSM Order to the Transfer
        self.picking_out.write({"fsm_order_id": self.fsm_order_1.id})
        # Test no vehicle is on the transfer
        self.assertFalse(self.picking_out.fsm_vehicle_id)
        # Write the bad vehicle to the FSM Order
        with self.assertRaises(UserError):
            self.fsm_order_1.write({"vehicle_id": self.fsm_veh_bad_loc.id})
        # Write good vehicle to the FSM Order
        self.fsm_order_1.write({"vehicle_id": self.fsm_veh_1.id})
        # Test same vehicle is on the transfer
        self.assertEqual(self.picking_out.fsm_vehicle_id, self.fsm_veh_1)
        # Test correct vehicle storage location is on the transfer
        move_line = self.move.move_line_ids
        self.assertEqual(move_line.location_dest_id, self.veh_1_loc)
        # confirm the transfer
        move_line.qty_done = 8.0
        self.picking_out._action_done()
        # test moves are done
        self.assertEqual(move_line.state, "done")
