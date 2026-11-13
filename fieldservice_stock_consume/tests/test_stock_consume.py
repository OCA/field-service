# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestFsmStockConsume(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["fsm.order"].create(
            {"location_id": cls.env.ref("fieldservice.test_location").id}
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.product = cls.env["product.product"].create(
            {"name": "Spare Part", "type": "consu"}
        )

    def _wizard(self, with_line=True):
        wizard = (
            self.env["fsm.stock.consume"]
            .with_context(active_model="fsm.order", active_id=self.order.id)
            .create({"warehouse_id": self.warehouse.id})
        )
        self.assertEqual(wizard.order_id, self.order)
        if with_line:
            self.env["fsm.stock.consume.line"].create(
                {
                    "wizard_id": wizard.id,
                    "product_id": self.product.id,
                    "product_qty": 2.0,
                    "product_uom_id": self.product.uom_id.id,
                }
            )
        return wizard

    def test_consume_creates_linked_delivery(self):
        wizard = self._wizard()
        action = wizard.action_confirm()
        picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(picking.origin, self.order.name)
        self.assertEqual(picking.group_id.fsm_order_id, self.order)
        self.assertEqual(picking.move_ids.product_id, self.product)
        self.assertEqual(picking.move_ids.product_uom_qty, 2.0)
        self.assertEqual(picking.move_ids.fsm_order_id, self.order)
        self.assertEqual(self.order.move_ids, picking.move_ids)
        self.assertNotEqual(picking.state, "draft")

    def test_consume_as_technician_without_stock_rights(self):
        technician = new_test_user(
            self.env,
            login="fsm_tech_no_stock",
            groups="fieldservice.group_fsm_user,base.group_user",
        )
        self.assertFalse(technician.has_group("stock.group_stock_user"))
        self.order.warehouse_id = self.warehouse
        wizard = (
            self.env["fsm.stock.consume"]
            .with_user(technician)
            .with_context(active_model="fsm.order", active_id=self.order.id)
            .create(
                {
                    "line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "product_qty": 3.0,
                                "product_uom_id": self.product.uom_id.id,
                            }
                        )
                    ]
                }
            )
        )
        self.assertEqual(wizard.warehouse_id, self.warehouse)
        action = wizard.action_confirm()
        picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(picking.move_ids.product_uom_qty, 3.0)
        self.assertEqual(picking.location_id, self.warehouse.lot_stock_id)
        self.assertEqual(picking.move_ids.fsm_order_id, self.order)

    def test_consume_without_lines_raises(self):
        wizard = self._wizard(with_line=False)
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_line_onchange_sets_uom(self):
        wizard = self._wizard(with_line=False)
        line = self.env["fsm.stock.consume.line"].new(
            {"wizard_id": wizard.id, "product_id": self.product.id}
        )
        line._onchange_product_id()
        self.assertEqual(line.product_uom_id, self.product.uom_id)

    def test_default_get_without_order_context(self):
        res = self.env["fsm.stock.consume"].default_get(["order_id", "warehouse_id"])
        self.assertNotIn("order_id", res)

    def test_default_get_uses_order_warehouse(self):
        self.order.warehouse_id = self.warehouse
        wizard = (
            self.env["fsm.stock.consume"]
            .with_context(active_model="fsm.order", active_id=self.order.id)
            .create({})
        )
        self.assertEqual(wizard.warehouse_id, self.warehouse)

    def test_default_get_order_without_warehouse(self):
        self.order.warehouse_id = False
        wizard = (
            self.env["fsm.stock.consume"]
            .with_context(active_model="fsm.order", active_id=self.order.id)
            .create({"warehouse_id": self.warehouse.id})
        )
        self.assertEqual(wizard.order_id, self.order)

    def test_consume_warehouse_without_delivery_type_raises(self):
        wizard = self._wizard()
        self.warehouse.out_type_id = False
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_line_onchange_without_product_keeps_uom(self):
        line = self.env["fsm.stock.consume.line"].new({})
        line._onchange_product_id()
        self.assertFalse(line.product_uom_id)

    def test_reuses_existing_procurement_group(self):
        wizard = self._wizard()
        wizard.action_confirm()
        group = self.order.procurement_group_id
        wizard2 = self._wizard()
        wizard2.action_confirm()
        self.assertEqual(self.order.procurement_group_id, group)
