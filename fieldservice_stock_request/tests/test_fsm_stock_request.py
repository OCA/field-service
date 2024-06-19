# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import datetime

from odoo import fields
from odoo.exceptions import UserError

from odoo.addons.fieldservice_stock.tests.test_fsm_stock import TestFSMStockCommon


class TestFSMStockRequest(TestFSMStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking in test
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Setup for Stock Request
        cls.StockRequest = cls.env["stock.request"]
        cls.StockRequestOrder = cls.env["stock.request.order"]
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.Product = cls.env["product.product"]

        cls.product_1 = cls.Product.create(
            {
                "name": "Product 1",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.product_2 = cls.Product.create(
            {
                "name": "Product 2",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.company_id.id)], limit=1
        )
        cls.ressuply_loc = cls.env["stock.location"].create(
            {
                "name": "Ressuply",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.stock_request_user_group = cls.env.ref(
            "stock_request.group_stock_request_user"
        )
        cls.fsm_dispatcher_group = cls.env.ref("fieldservice.group_fsm_dispatcher")
        cls.group_stock_request_manager = cls.env.ref(
            "stock_request.group_stock_request_manager"
        )
        cls.stock_request_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "stock_request_user1",
                    "password": "demo",
                    "login": "stock_request_user1",
                    "email": "@".join(["stock_request_user", "test.com"]),
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                cls.stock_request_user_group.id,
                                cls.fsm_dispatcher_group.id,
                            ],
                        )
                    ],
                    "company_ids": [(6, 0, [cls.env.user.company_id.id])],
                }
            )
        )
        cls.stock_request_manager = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "stock_request_manager1",
                    "password": "demo",
                    "login": "stock_request_manager1",
                    "email": "@".join(["stock_request_user", "test.com"]),
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                cls.fsm_dispatcher_group.id,
                                cls.group_stock_request_manager.id,
                            ],
                        )
                    ],
                    "company_ids": [(6, 0, [cls.env.user.company_id.id])],
                }
            )
        )

    def test_fsm_order_stock_request(self):
        # Create a new FS Order and add to it some SR
        FSO = self.FSMOrder.create({"location_id": self.test_location.id})
        fsm_order = self.FSMOrder.create({"location_id": self.test_location.id})

        self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": FSO.warehouse_id.id,
            }
        )
        SR_1 = self.StockRequest.create(
            {
                "warehouse_id": FSO.warehouse_id.id,
                "location_id": FSO.inventory_location_id.id,
                "product_id": self.product_1.id,
                "product_uom_qty": 1,
                "product_uom_id": self.product_1.uom_id.id,
                "fsm_order_id": FSO.id,
                "direction": "outbound",
                "expected_date": datetime.datetime.now(),
                "picking_policy": "direct",
            }
        )
        # After create the SR linked to FSO, validate a SRO
        # was created and linked to this FSO
        SRO = self.StockRequestOrder.search(
            [("fsm_order_id", "=", FSO.id), ("warehouse_id", "=", FSO.warehouse_id.id)]
        )
        self.assertTrue(SRO)
        SRO._onchange_location_id()

        # Add a second SR to the FSO
        SR_2 = self.StockRequest.create(
            {
                "warehouse_id": FSO.warehouse_id.id,
                "location_id": FSO.inventory_location_id.id,
                "product_id": self.product_2.id,
                "product_uom_qty": 4,
                "product_uom_id": self.product_2.uom_id.id,
                "fsm_order_id": FSO.id,
                "direction": "outbound",
                "expected_date": datetime.datetime.now(),
                "picking_policy": "direct",
            }
        )
        # After create the 2nd SR linked to same FSO, validate
        # this SR is assigned to the same SRO
        self.assertEqual(SR_2.order_id, SRO)
        with self.assertRaises(UserError):
            fsm_order.action_request_cancel()

        # Cancel the SRs from FSO. Confirm SR are cancelled
        FSO.action_request_cancel()
        self.assertEqual(FSO.request_stage, "cancel")
        self.assertEqual(SR_1.state, "cancel")
        self.assertEqual(SR_2.state, "cancel")
        self.assertEqual(SRO.state, "cancel")

        with self.assertRaises(UserError):
            fsm_order.action_request_draft()

        # Set the SR to draft. Confirm SR are draft
        FSO.action_request_draft()
        self.assertEqual(FSO.request_stage, "draft")
        self.assertEqual(SR_1.state, "draft")
        self.assertEqual(SR_2.state, "draft")
        self.assertEqual(SRO.state, "draft")

        # Submit the SRs from FSO. Confirm FSO request, SR & SRO are submitted
        FSO.action_request_submit()
        self.assertEqual(FSO.request_stage, "submitted")
        self.assertEqual(SR_1.state, "submitted")
        self.assertEqual(SR_2.state, "submitted")
        self.assertEqual(SRO.state, "submitted")

        with self.assertRaises(UserError):
            fsm_order.action_request_submit()
        self.StockRequest.create(
            {
                "warehouse_id": fsm_order.warehouse_id.id,
                "location_id": fsm_order.inventory_location_id.id,
                "product_id": self.product_2.id,
                "product_uom_qty": 4,
                "product_uom_id": self.product_2.uom_id.id,
                "fsm_order_id": fsm_order.id,
                "direction": "outbound",
                "expected_date": datetime.datetime.now(),
                "picking_policy": "direct",
            }
        )
        fsm_order.stock_request_ids.order_id = False
        fsm_order.action_request_cancel()
        fsm_order.action_request_draft()
        fsm_order.action_request_submit()

    def test_stock_move_line(self):
        expected_date = fields.Datetime.now()
        FSO = self.FSMOrder.create({"location_id": self.test_location.id})
        procurement_group = self.env["procurement.group"].create({"name": "TEST"})
        self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": FSO.warehouse_id.id,
            }
        )
        vals = {
            "company_id": self.env.user.company_id.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "requested_by": self.env.uid,
        }
        order = self.env["stock.request.order"].with_user(self.env.user).create(vals)
        self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": FSO.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "outbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        order.with_user(self.stock_request_manager).write(
            {"stock_request_ids": [(6, 0, FSO.stock_request_ids.ids)]}
        )
        stock_request = order.stock_request_ids
        order.procurement_group_id = procurement_group
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 1.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.warehouse.in_type_id.id,
            }
        )
        self.env["procurement.group"].run(
            [
                procurement_group.Procurement(
                    self.product_1,
                    2.0,
                    self.product_1.uom_id,
                    self.warehouse.lot_stock_id,
                    "wave_part_1",
                    "wave_part_1",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": procurement_group},
                )
            ]
        )
        order.with_user(self.stock_request_manager).action_confirm()

        self.env["stock.quant"].create(
            {
                "product_id": self.product_1.id,
                "location_id": self.ressuply_loc.id,
                "quantity": 5.0,
            }
        )
        picking = stock_request.picking_ids[0]
        picking.with_user(self.stock_request_manager).action_confirm()
        picking.with_user(self.stock_request_manager).action_assign()
        packout1 = picking.move_line_ids[0]
        packout1.quantity = 5
        picking.with_user(self.stock_request_manager)._action_done()

    def test_08_stock_request(self):
        expected_date = fields.Datetime.now()
        FSO = self.FSMOrder.create({"location_id": self.test_location.id})
        self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": FSO.warehouse_id.id,
            }
        )
        stock_request = self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": FSO.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "inbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        stock_request._onchange_location_id()
        stock_request.prepare_stock_request_order_values()

    def test_stock_request_confirm(self):
        expected_date = fields.Datetime.now()
        FSO = self.FSMOrder.create({"location_id": self.test_location.id})
        procurement_group = self.env["procurement.group"].create({"name": "TEST"})
        self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": FSO.warehouse_id.id,
            }
        )
        vals = {
            "company_id": self.env.user.company_id.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "requested_by": self.env.uid,
            "fsm_order_id": FSO.id,
        }
        order = self.env["stock.request.order"].with_user(self.env.user).create(vals)
        self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": FSO.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "outbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        order.with_user(self.stock_request_manager).write(
            {"stock_request_ids": [(6, 0, FSO.stock_request_ids.ids)]}
        )
        stock_request = order.stock_request_ids
        order.procurement_group_id = procurement_group
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 1.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.warehouse.in_type_id.id,
            }
        )
        self.env["procurement.group"].run(
            [
                procurement_group.Procurement(
                    self.product_1,
                    2.0,
                    self.product_1.uom_id,
                    self.warehouse.lot_stock_id,
                    "wave_part_1",
                    "wave_part_1",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": procurement_group},
                )
            ]
        )
        order.write({"fsm_order_id": FSO.id})
        order.action_confirm()
        stock_request._action_confirm()

        order_without_fsm = order.copy({"fsm_order_id": False})
        order_without_fsm.action_confirm()

    def test_stock_request_confirm_with_FSM(self):
        expected_date = fields.Datetime.now()
        FSO = self.FSMOrder.create({"location_id": self.test_location.id})
        self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": FSO.warehouse_id.id,
            }
        )
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 1.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.warehouse.in_type_id.id,
            }
        )
        procurement_group = self.env["procurement.group"].create({"name": "TEST"})
        self.env["procurement.group"].run(
            [
                procurement_group.Procurement(
                    self.product_1,
                    2.0,
                    self.product_1.uom_id,
                    self.warehouse.lot_stock_id,
                    "wave_part_1",
                    "wave_part_1",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": procurement_group},
                )
            ]
        )
        stock_request = self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": FSO.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "inbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        stock_request.order_id.action_confirm()
