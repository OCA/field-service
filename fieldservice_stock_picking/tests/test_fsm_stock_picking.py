# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.exceptions import UserError

from odoo.addons.fieldservice_stock.tests.test_fsm_stock import TestFSMStockCommon


class TestFSMStockPicking(TestFSMStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Product = cls.env["product.product"]
        cls.product_1 = cls.Product.create({"name": "Material 1", "type": "product"})
        cls.product_2 = cls.Product.create({"name": "Material 2", "type": "product"})
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.company_id.id)], limit=1
        )

    def test_default_picking_types(self):
        order = self.env["fsm.order"].create({"location_id": self.test_location.id})
        # Defaults come from the warehouse operation types
        self.assertEqual(order.outgoing_picking_type_id, order.warehouse_id.out_type_id)
        self.assertEqual(order.incoming_picking_type_id, order.warehouse_id.in_type_id)

    def test_template_presets_picking_types(self):
        out_type = self.warehouse.out_type_id.copy({"name": "FSM Out"})
        in_type = self.warehouse.in_type_id.copy({"name": "FSM In"})
        template = self.env["fsm.template"].create(
            {
                "name": "FSM material template",
                "outgoing_picking_type_id": out_type.id,
                "incoming_picking_type_id": in_type.id,
            }
        )
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "template_id": template.id,
            }
        )
        # The template presets win over the warehouse operation types
        self.assertEqual(order.outgoing_picking_type_id, out_type)
        self.assertEqual(order.incoming_picking_type_id, in_type)
        self.assertNotEqual(order.outgoing_picking_type_id, self.warehouse.out_type_id)

    def test_template_change_overrides_warehouse_default(self):
        out_type = self.warehouse.out_type_id.copy({"name": "FSM Out"})
        template = self.env["fsm.template"].create(
            {
                "name": "FSM outgoing template",
                "outgoing_picking_type_id": out_type.id,
            }
        )
        order = self.env["fsm.order"].create({"location_id": self.test_location.id})
        # Without a template, the warehouse defaults apply
        self.assertEqual(order.outgoing_picking_type_id, self.warehouse.out_type_id)
        # Setting a template with a preset rewrites the order operation type
        order.template_id = template
        self.assertEqual(order.outgoing_picking_type_id, out_type)
        # The template has no incoming preset, so the warehouse default stays
        self.assertEqual(order.incoming_picking_type_id, self.warehouse.in_type_id)

    def test_create_outgoing_and_incoming_transfers(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "outgoing_line_ids": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 3}),
                ],
                "incoming_line_ids": [
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 2}),
                ],
            }
        )
        order.action_create_transfers()

        # One outgoing and one incoming picking, linked through the group
        self.assertEqual(order.delivery_count, 1)
        self.assertEqual(order.return_count, 1)
        self.assertEqual(len(order.picking_ids), 2)
        for picking in order.picking_ids:
            self.assertEqual(picking.fsm_order_id, order)
            self.assertEqual(picking.group_id, order.procurement_group_id)

        out_picking = order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        in_picking = order.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        # Outgoing goes to the inventory (customer) location of the FSM location
        self.assertEqual(
            out_picking.location_dest_id,
            order.location_id.inventory_location_id,
        )
        # Incoming comes from the inventory (customer) location
        self.assertEqual(
            in_picking.location_id,
            order.location_id.inventory_location_id,
        )
        # Moves are linked back to the FSM order and to the lines
        self.assertEqual(out_picking.move_ids.product_id, self.product_1)
        self.assertEqual(out_picking.move_ids.fsm_order_id, order)
        self.assertEqual(order.outgoing_line_ids.move_id, out_picking.move_ids)
        self.assertEqual(order.incoming_line_ids.move_id, in_picking.move_ids)

    def test_no_recreate_for_existing_lines(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "outgoing_line_ids": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 1}),
                ],
            }
        )
        order.action_create_transfers()
        self.assertEqual(order.delivery_count, 1)
        # Calling again with no new lines raises (nothing to transfer)
        with self.assertRaises(UserError):
            order.action_create_transfers()
        # Adding a new line creates a second transfer only for that line
        order.write(
            {
                "outgoing_line_ids": [
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 5}),
                ]
            }
        )
        order.action_create_transfers()
        self.assertEqual(order.delivery_count, 2)

    def test_missing_picking_type_raises(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "outgoing_line_ids": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 1}),
                ],
            }
        )
        order.outgoing_picking_type_id = False
        with self.assertRaises(UserError):
            order.action_create_transfers()

    def test_standard_flow_validate_picking(self):
        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "outgoing_line_ids": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 2}),
                ],
            }
        )
        order.action_create_transfers()
        picking = order.picking_ids
        # Picking is created in draft and processed via the standard flow
        self.assertEqual(picking.state, "draft")
        picking.action_confirm()
        for move_line in picking.move_ids:
            move_line.quantity_done = move_line.product_uom_qty
        picking._action_done()
        self.assertEqual(picking.state, "done")
