# Copyright (C) 2020, Brian McMaster
# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMStockCommon(FSMCommon):
    def setUp(cls):
        super().setUp()
        cls.location = cls.env["fsm.location"]
        cls.FSMOrder = cls.env["fsm.order"]
        cls.Product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "uom_id": cls.env.ref("uom.product_uom_meter").id,
            }
        )
        cls.stock_cust_loc = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.partner_1 = (
            cls.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "Partner 1"})
        )
        cls.customer = cls.env["res.partner"].create({"name": "SuperPartner"})

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        hours_diff = 100
        pick_list = []
        order_in_pickings = []
        order_pick_list2 = []
        date_start = fields.Datetime.today()
        order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
        order2 = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=50),
                "request_early": fields.Datetime.today(),
            }
        )
        order3 = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=50),
                "request_early": fields.Datetime.today(),
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "location_dest_id": self.stock_location.id,
                "location_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "fsm_order_id": order3.id,
            }
        )
        self.picking1 = self.env["stock.picking"].create(
            {
                "location_dest_id": self.stock_location.id,
                "location_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "fsm_order_id": order3.id,
            }
        )
        order_in_pickings.append(self.picking.id)
        order_in_pickings.append(self.picking1.id)
        self.in_picking = self.env["stock.picking"].create(
            {
                "location_dest_id": self.stock_location.id,
                "location_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "fsm_order_id": order.id,
            }
        )
        order_pick_list2.append(self.in_picking.id)
        self.out_picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        order_pick_list2.append(self.out_picking.id)
        self.out_picking2 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "fsm_order_id": order2.id,
            }
        )
        pick_list.append(self.out_picking2.id)
        self.out_picking3 = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "fsm_order_id": order2.id,
            }
        )
        rule = self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": warehouse.reception_route_id.id,
                "location_dest_id": warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 9.0,
                "procure_method": "make_to_stock",
                "picking_type_id": warehouse.in_type_id.id,
            }
        )
        rule._get_stock_move_values(
            self.Product,
            1,
            self.Product.uom_id,
            warehouse.lot_stock_id,
            "name",
            "origin",
            self.env.user.company_id,
            {"date_planned": fields.Datetime.today()},
        )
        pick_list.append(self.out_picking3.id)
        order2.picking_ids = [(6, 0, pick_list)]
        order3.picking_ids = [(6, 0, order_in_pickings)]
        order.picking_ids = [(6, 0, order_pick_list2)]
        order._compute_picking_ids()
        order.location_id._onchange_parent_id()
        order._default_warehouse_id()
        order.action_view_delivery()
        order2.action_view_delivery()
        order3.action_view_returns()
        order.action_view_returns()

    def test_action_view_no_pickings(self):
        """
        action_view_delivery/returns return plain action when order has no pickings.
        """
        date_start = fields.Datetime.today()
        order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=1),
                "request_early": date_start,
            }
        )
        # No pickings attached — elif pickings: evaluates to False
        action_delivery = order.action_view_delivery()
        self.assertIsInstance(action_delivery, dict)
        action_returns = order.action_view_returns()
        self.assertIsInstance(action_returns, dict)

    def test_compute_inventory_location_id(self):
        """inventory_location_id is inherited from parent_id when parent is set."""
        stock_loc = self.env.ref("stock.stock_location_stock")
        parent_loc = self.env["fsm.location"].create(
            {
                "name": "Parent Location",
                "partner_id": self.partner_1.id,
                "owner_id": self.partner_1.id,
            }
        )
        # Write after creation so the stored compute doesn't race with the value
        parent_loc.inventory_location_id = stock_loc
        child_loc = self.env["fsm.location"].create(
            {
                "name": "Child Location",
                "partner_id": self.partner_1.id,
                "owner_id": self.partner_1.id,
            }
        )
        # Setting parent_id triggers _compute_inventory_location_id on child
        child_loc.parent_id = parent_loc
        self.assertEqual(child_loc.inventory_location_id, stock_loc)

    def test_onchange_person_id_warehouse(self):
        """_onchange_person_id sets warehouse from worker and skips completed orders."""
        date_start = fields.Datetime.today()
        warehouse2 = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse 2",
                "code": "TW2",
            }
        )
        self.test_person.default_warehouse_id = warehouse2

        # Normal order: warehouse should be updated from person's default
        order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=1),
                "request_early": date_start,
                "person_id": self.test_person.id,
            }
        )
        order.person_id = self.test_person
        order._onchange_person_id()
        self.assertEqual(order.warehouse_id, warehouse2)

        # Completed order: warehouse must not change
        completed_stage = self.env.ref("fieldservice.fsm_stage_completed")
        order.with_context(bypass_order_completed_stage=True).write(
            {"stage_id": completed_stage.id}
        )
        original_warehouse = order.warehouse_id
        order.person_id = False
        order._onchange_person_id()
        self.assertEqual(order.warehouse_id, original_warehouse)
