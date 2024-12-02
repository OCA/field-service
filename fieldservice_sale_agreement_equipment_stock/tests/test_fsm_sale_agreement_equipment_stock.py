# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestFieldServiceSaleAgreementEquipmentStock(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product = cls.env["product.product"].create(
            {
                "name": "FSM Product",
                "type": "product",
                "tracking": "serial",
                "create_fsm_equipment": True,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.main_partner").id,
                "agreement_id": cls.env.ref("agreement.market1").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        cls.order.warehouse_id.out_type_id.use_create_lots = True
        cls.order.warehouse_id.out_type_id.create_fsm_equipment = True

    def test_propagate_agreement_id(self):
        self.order.action_confirm()
        self.assertTrue(self.order.picking_ids, "The Picking should've been created")
        stock_move = self.order.picking_ids.move_ids
        stock_move._set_quantity_done(1.0)
        stock_move.picked = True
        stock_move_line = stock_move.move_line_ids
        stock_move_line.lot_name = "TEST"
        self.order.picking_ids.button_validate()
        self.assertTrue(
            stock_move_line.lot_id.fsm_equipment_id,
            "The FSM Equipment should've been created",
        )
        self.assertEqual(
            self.order.agreement_id,
            stock_move_line.lot_id.fsm_equipment_id.agreement_id,
            "The FSM Equipment should have the same agreement as the Sale Order",
        )
