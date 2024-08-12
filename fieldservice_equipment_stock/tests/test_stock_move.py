# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


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
            {"name": "templAB", "uom_id": self.uom_unit.id}
        )

        # Create product A and B
        productA = self.env["product.product"].create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
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
                "name": "MOVE INCOMING -> STOCK ",
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
