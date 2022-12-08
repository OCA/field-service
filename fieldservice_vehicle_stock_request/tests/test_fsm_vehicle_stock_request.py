# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMVehicaleStockRequest(TransactionCase):
    def setUp(self):
        super(TestFSMVehicaleStockRequest, self).setUp()
        # disable tracking in test
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        # Setup for Stock Request
        self.StockRequest = self.env["stock.request"]
        self.StockRequestOrder = self.env["stock.request.order"]
        self.StockPickingType = self.env["stock.picking.type"]
        self.FSMOrder = self.env["fsm.order"]
        self.ProcurementGroup = self.env["procurement.group"]
        self.company1 = self.env.user.company_id.id
        self.warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company1)], limit=1
        )
        self.test_location = self.env.ref("fieldservice.test_location")
        self.test_partner = self.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
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
        self.test_vehicle = self.env["fsm.vehicle"].create(
            {
                "name": "Test Vehicle",
                "inventory_location_id": self.test_location.id,
                "model_id": model.id,
            }
        )

        self.test_worker = self.env["fsm.person"].create(
            {
                "name": "Test Wokrer",
                "email": "tw@email.com",
                "vehicle_id": self.test_vehicle.id,
            }
        )
        self.product_1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "tracking": "serial",
            }
        )
        self.route = self.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": self.env.user.company_id.id,
                "sequence": 10,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": self.ref("stock.picking_type_out"),
                            "location_src_id": self.ref("stock.stock_location_stock"),
                            "location_id": self.ref("stock.stock_location_customers"),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": self.ref("stock.picking_type_out"),
                            "location_src_id": self.warehouse.lot_stock_id.id,
                            "location_id": self.ref("stock.stock_location_customers"),
                        },
                    ),
                ],
            }
        )
        self.ressuply_loc = self.env["stock.location"].create(
            {
                "name": "Ressuply",
                "location_id": self.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": self.env.user.company_id.id,
            }
        )
        self.new_pick_type = self.StockPickingType.create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": self.warehouse.id,
                "company_id": self.company1,
            }
        )

    def test_01_request_action_confirm(self):
        expected_date = fields.Datetime.now()
        self.test_order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "company_id": self.company1,
                "warehouse_id": self.warehouse.id,
                "person_id": self.test_worker.id,
                "inventory_location_id": self.test_location.id,
                "vehicle_id": self.test_vehicle.id,
            }
        )
        self.picking = (
            self.env["stock.picking"]
            .with_context(company_id=self.company1)
            .create(
                {
                    "name": "Stock Picking",
                    "location_id": self.test_location.id,
                    "location_dest_id": self.test_location.id,
                    "move_type": "direct",
                    "picking_type_id": self.new_pick_type.id,
                }
            )
        )
        vals = {
            "company_id": self.env.user.company_id.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "requested_by": self.env.uid,
            "fsm_order_id": self.test_order.id,
        }
        order = self.StockRequestOrder.with_user(self.env.user).create(vals)
        self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": self.test_order.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "outbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        order.write(
            {"stock_request_ids": [(6, 0, self.test_order.stock_request_ids.ids)]}
        )
        stock_request = order.stock_request_ids
        procurement_group = self.ProcurementGroup.create({"name": "TEST"})
        order.procurement_group_id = procurement_group
        self.product_1.route_ids = [(6, 0, self.route.ids)]
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 1.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.env.ref(
                    "fieldservice_vehicle_stock.picking_type_vehicle_to_location"
                ).id,
            }
        )
        self.ProcurementGroup.run(
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
        order.action_confirm()
        stock_request._action_confirm()
        stock_request.action_assign()
        stock_request.action_show_details()

    def test_02_request_action_deliver(self):
        product_2 = self.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
            }
        )
        expected_date = fields.Datetime.now()
        self.test_order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "company_id": self.company1,
                "warehouse_id": self.warehouse.id,
                "person_id": self.test_worker.id,
                "inventory_location_id": self.test_location.id,
                "vehicle_id": self.test_vehicle.id,
            }
        )
        self.picking = (
            self.env["stock.picking"]
            .with_context(company_id=self.company1)
            .create(
                {
                    "name": "Stock Picking",
                    "location_id": self.test_location.id,
                    "location_dest_id": self.test_location.id,
                    "move_type": "direct",
                    "picking_type_id": self.new_pick_type.id,
                }
            )
        )
        vals = {
            "company_id": self.env.user.company_id.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "requested_by": self.env.uid,
            "fsm_order_id": self.test_order.id,
        }
        order = self.StockRequestOrder.with_user(self.env.user).create(vals)
        self.StockRequest.create(
            {
                "product_id": product_2.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": self.test_order.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "outbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
            },
        )
        order.write(
            {"stock_request_ids": [(6, 0, self.test_order.stock_request_ids.ids)]}
        )
        stock_request = order.stock_request_ids
        procurement_group = self.ProcurementGroup.create({"name": "TEST"})
        order.procurement_group_id = procurement_group
        product_2.route_ids = [(6, 0, self.route.ids)]
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 1.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.env.ref(
                    "fieldservice_vehicle_stock.picking_type_vehicle_to_location"
                ).id,
            }
        )
        self.ProcurementGroup.run(
            [
                procurement_group.Procurement(
                    product_2,
                    2.0,
                    product_2.uom_id,
                    self.warehouse.lot_stock_id,
                    "wave_part_1",
                    "wave_part_1",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": procurement_group},
                )
            ]
        )
        order.action_confirm()
        stock_request._action_confirm()
        stock_request.action_deliver()
        stock_request.action_assign()
        stock_request.action_show_details()

    def test_03_multi_request_action_confirm(self):
        expected_date = fields.Datetime.now()
        self.test_order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "company_id": self.company1,
                "warehouse_id": self.warehouse.id,
                "person_id": self.test_worker.id,
                "inventory_location_id": self.test_location.id,
                "vehicle_id": self.test_vehicle.id,
            }
        )
        self.picking = (
            self.env["stock.picking"]
            .with_context(company_id=self.company1)
            .create(
                {
                    "name": "Stock Picking",
                    "location_id": self.test_location.id,
                    "location_dest_id": self.test_location.id,
                    "move_type": "direct",
                    "picking_type_id": self.new_pick_type.id,
                }
            )
        )
        vals = {
            "company_id": self.env.user.company_id.id,
            "warehouse_id": self.warehouse.id,
            "location_id": self.warehouse.lot_stock_id.id,
            "expected_date": expected_date,
            "requested_by": self.env.uid,
            "fsm_order_id": self.test_order.id,
        }
        order = self.StockRequestOrder.with_user(self.env.user).create(vals)
        self.StockRequest.create(
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5.0,
                "fsm_order_id": self.test_order.id,
                "company_id": self.env.user.company_id.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": expected_date,
                "direction": "outbound",
                "picking_policy": "direct",
                "requested_by": self.env.uid,
                "order_id": order.id,
            },
        )
        order.write(
            {"stock_request_ids": [(6, 0, self.test_order.stock_request_ids.ids)]}
        )
        stock_request = order.stock_request_ids
        procurement_group = self.ProcurementGroup.create({"name": "TEST"})
        order.procurement_group_id = procurement_group
        self.product_1.route_ids = [(6, 0, self.route.ids)]
        self.env["stock.rule"].create(
            {
                "name": "Rule Supplier",
                "route_id": self.warehouse.reception_route_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "delay": 2.0,
                "procure_method": "make_to_stock",
                "picking_type_id": self.env.ref(
                    "fieldservice_vehicle_stock.picking_type_vehicle_to_location"
                ).id,
            }
        )
        self.ProcurementGroup.run(
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
        order.action_confirm()
        stock_request._action_confirm()
        stock_request.action_assign()
        stock_request.action_show_details()
