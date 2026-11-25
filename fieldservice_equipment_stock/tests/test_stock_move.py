# Copyright (C) 2021 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestStockMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Move = cls.env["stock.move"]
        cls.stock_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_action_done(self):
        # Create product template
        templateAB = self.env["product.template"].create(
            {
                "name": "templAB",
                "uom_id": self.uom_unit.id,
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
            }
        )

        # Create product A and B
        productA = self.env["product.product"].create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "uom_id": self.uom_unit.id,
                "default_code": "A",
                "product_tmpl_id": templateAB.id,
            }
        )

        # Create a stock move from INCOMING to STOCK
        stockMoveInA = self.env["stock.move"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": productA.id,
                "product_uom": productA.uom_id.id,
                "product_uom_qty": 2,
            }
        )

        stockMoveInA.quantity = stockMoveInA.product_uom_qty
        stockMoveInA._action_confirm()
        stockMoveInA._action_assign()
        stockMoveInA.picked = True
        stockMoveInA._action_done()

        self.assertEqual("done", stockMoveInA.state)

    def test_action_done_stock_user_creates_equipment(self):
        """A warehouse user who is not an FSM manager can validate a delivery.

        Equipment creation is a side effect of the stock operation.
        """
        stock_user = self.env["res.users"].create(
            {
                "name": "Warehouse Dispatcher",
                "login": "warehouse_dispatcher",
                "email": "warehouse_dispatcher@example.com",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("stock.group_stock_user").id,
                            self.env.ref("fieldservice.group_fsm_dispatcher").id,
                        ],
                    )
                ],
            }
        )
        self.assertTrue(stock_user.has_group("stock.group_stock_user"))
        self.assertTrue(stock_user.has_group("fieldservice.group_fsm_dispatcher"))
        self.assertFalse(stock_user.has_group("fieldservice.group_fsm_manager"))

        picking_type = self.env.ref("stock.picking_type_out")
        picking_type.create_fsm_equipment = True
        src = picking_type.default_location_src_id
        dest = picking_type.default_location_dest_id
        product = self.env["product.product"].create(
            {
                "name": "Serialized pump",
                "type": "consu",
                "is_storable": True,
                "tracking": "serial",
                "create_fsm_equipment": True,
            }
        )
        lot = self.env["stock.lot"].create(
            {
                "name": "SN-1628",
                "product_id": product.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, src, 1.0, lot_id=lot
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.quantity = 1
        picking.move_ids.picked = True
        picking.with_user(stock_user).button_validate()

        self.assertEqual(picking.state, "done")
        self.assertTrue(lot.fsm_equipment_id)
        self.assertEqual(lot.fsm_equipment_id.product_id, product)
        self.assertEqual(lot.fsm_equipment_id.lot_id, lot)
