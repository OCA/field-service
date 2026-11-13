# Copyright (C) 2022, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFSMVehicleStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set up inventory locations
        cls.veh_parent_loc = cls.env.ref(
            "fieldservice_vehicle_stock.stock_location_vehicle_storage"
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.veh_1_loc = cls.env["stock.location"].create(
            {
                "name": "Vehicle 1 Storage",
                "location_id": cls.veh_parent_loc.id,
                "usage": "internal",
            }
        )
        cls.veh_2_loc = cls.env["stock.location"].create(
            {
                "name": "Vehicle 2 Storage",
                "location_id": cls.veh_parent_loc.id,
                "usage": "internal",
            }
        )
        cls.non_vehicle_stock_loc = cls.env["stock.location"].create(
            {
                "name": "Other Stock Location",
                "location_id": cls.stock_location.id,
                "usage": "internal",
            }
        )

        # Set up FSM Vehicles with inventory locations
        cls.fsm_veh_1 = cls._create_vehicle("Vehicle 1", cls.veh_1_loc)
        cls.fsm_veh_2 = cls._create_vehicle("Vehicle 2", cls.veh_2_loc)
        cls.fsm_veh_bad_loc = cls._create_vehicle(
            "Vehicle with Incorrect Location", cls.non_vehicle_stock_loc
        )

        # Set up product and stock it to use for a transfer
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 100
        )

        # Set up a transfer using the operation type for vehicle loading
        cls.picking_type_id_loc_to_veh = cls.env.ref(
            "fieldservice_vehicle_stock.picking_type_output_to_vehicle"
        )
        cls.picking_type_id_veh_to_loc = cls.env.ref(
            "fieldservice_vehicle_stock.picking_type_vehicle_to_location"
        )
        cls.picking_out = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_id_loc_to_veh.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.veh_parent_loc.id,
            }
        )
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_id_veh_to_loc.id,
                "location_id": cls.veh_parent_loc.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.move_out = cls.env["stock.move"].create(
            {
                "name": "Test Vehicle Stock Move",
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.veh_parent_loc.id,
                "product_id": cls.product.id,
                "product_uom_qty": 8.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "picking_id": cls.picking_out.id,
            }
        )
        cls.move_in = cls.env["stock.move"].create(
            {
                "name": "Test Vehicle Stock Move",
                "location_id": cls.veh_parent_loc.id,
                "location_dest_id": cls.stock_location.id,
                "product_id": cls.product.id,
                "product_uom_qty": 8.0,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "picking_id": cls.picking_in.id,
            }
        )

        # Setup FSM Order
        cls.fsm_location = cls.env.ref("fieldservice.test_location")
        cls.fsm_order_1 = cls.env["fsm.order"].create(
            {
                "name": "FSM Order 1",
                "location_id": cls.fsm_location.id,
            }
        )
        cls.group = cls.env["procurement.group"].create(
            {"name": "FSM Order 1", "fsm_order_id": cls.fsm_order_1.id}
        )

    @classmethod
    def _create_vehicle(cls, name, location):
        # fieldservice_fleet makes the fleet vehicle mandatory
        needs_fleet = "fleet_vehicle_id" in cls.env["fsm.vehicle"]._fields
        fleet_vals = needs_fleet and {"fleet_vehicle_id": cls._create_fleet().id} or {}
        return cls.env["fsm.vehicle"].create(
            dict(fleet_vals, name=name, inventory_location_id=location.id)
        )

    @classmethod
    def _create_fleet(cls):
        fleet_model = cls.env["fleet.vehicle.model"].search([], limit=1)
        return cls.env["fleet.vehicle"].create({"model_id": fleet_model.id})

    def test_fsm_vehicle_stock_loc_to_veh(self):
        # 1. Test trasnfer from stock location to vehicle location
        # Test assing quantities to transfer w/out a vehicle
        with self.assertRaises(UserError):
            self.picking_out.action_assign()
        # Test confirm transfer w/out a vehicle
        with self.assertRaises(UserError):
            self.picking_out._action_done()
        # Write FSM Order to the Transfer
        self.picking_out.write(
            {"group_id": self.group.id, "fsm_order_id": self.fsm_order_1.id}
        )
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
        self.picking_out.action_assign()
        move_line = self.move_out.move_line_ids
        self.assertEqual(move_line.location_dest_id, self.veh_1_loc)
        # confirm the transfer
        move_line.write({"quantity": 8.0, "picked": True})
        self.picking_out._action_done()
        # test moves are done
        self.assertEqual(move_line.state, "done")

        # 2. Test transfer from vehicle location to stock location
        # Test assing quantities to transfer w/out a vehicle
        with self.assertRaises(UserError):
            self.picking_in.action_assign()
        # Test confirm transfer w/out a vehicle
        with self.assertRaises(UserError):
            self.picking_in._action_done()
        # Write FSM Order to the Transfer
        self.picking_in.write(
            {"group_id": self.group.id, "fsm_order_id": self.fsm_order_1.id}
        )
        # Test vehicle is on the transfer, as we updated earlier the FSM order's vehicle
        self.assertTrue(self.picking_in.fsm_vehicle_id)
        # Test same vehicle is on the transfer
        self.assertEqual(self.picking_in.fsm_vehicle_id, self.fsm_veh_1)
        # Test correct vehicle storage location is on the transfer
        self.picking_in.action_assign()
        move_line = self.move_in.move_line_ids
        self.assertEqual(move_line.location_id, self.veh_1_loc)
        # confirm the transfer
        move_line.write({"quantity": 8.0, "picked": True})
        self.picking_in._action_done()
        # test moves are done
        self.assertEqual(move_line.state, "done")

    def test_regular_picking_not_affected(self):
        picking_type = self.env.ref("stock.picking_type_internal")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.non_vehicle_stock_loc.id,
                "fsm_vehicle_id": self.fsm_veh_1.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Regular Move",
                "location_id": self.stock_location.id,
                "location_dest_id": self.non_vehicle_stock_loc.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "picking_id": picking.id,
            }
        )
        picking.action_assign()
        self.assertEqual(picking.location_dest_id, self.non_vehicle_stock_loc)

    def test_fsm_order_vehicle_skips_closed_pickings(self):
        self.picking_out.write(
            {"group_id": self.group.id, "fsm_order_id": self.fsm_order_1.id}
        )
        self.picking_out.action_cancel()
        self.fsm_order_1.write({"description": "No vehicle change"})
        self.assertFalse(self.picking_out.fsm_vehicle_id)
        self.fsm_order_1.write({"vehicle_id": self.fsm_veh_2.id})
        self.assertFalse(self.picking_out.fsm_vehicle_id)

    def test_vehicle_storage_already_set(self):
        self.picking_out.write(
            {
                "fsm_vehicle_id": self.fsm_veh_2.id,
            }
        )
        self.assertEqual(self.picking_out.location_dest_id, self.veh_2_loc)
        self.picking_out.update_vehicle_storage()
        self.assertEqual(self.picking_out.location_dest_id, self.veh_2_loc)
        self.picking_in.write({"fsm_vehicle_id": self.fsm_veh_2.id})
        self.assertEqual(self.picking_in.location_id, self.veh_2_loc)
        self.picking_in.update_vehicle_storage()
        self.assertEqual(self.picking_in.location_id, self.veh_2_loc)
