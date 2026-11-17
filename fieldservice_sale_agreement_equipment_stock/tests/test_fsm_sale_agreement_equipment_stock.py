# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestFieldServiceSaleAgreementEquipmentStock(TestSaleCommon):
    @classmethod
    def get_default_groups(cls):
        groups = super().get_default_groups()
        return groups | cls.env.ref("fieldservice.group_fsm_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "FSM SA Partner"})
        cls.agreement = cls.env["agreement"].create(
            {
                "name": "Test Agreement",
                "code": "TEST-AGR-EQ",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
                "partner_id": cls.partner.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "FSM Product",
                "type": "consu",
                "is_storable": True,
                "tracking": "serial",
                "create_fsm_equipment": True,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "agreement_id": cls.agreement.id,
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

    def test_prepare_equipment_values_with_agreement(self):
        """Directly cover prepare_equipment_values when a sale order is linked."""
        self.order.action_confirm()
        stock_move = self.order.picking_ids.move_ids
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-AGR",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        move_line = self.env["stock.move.line"].create(
            {
                "move_id": stock_move.id,
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "location_id": stock_move.location_id.id,
                "location_dest_id": stock_move.location_dest_id.id,
                "lot_id": lot.id,
                "quantity": 1,
            }
        )
        values = stock_move.prepare_equipment_values(move_line)
        self.assertEqual(values.get("agreement_id"), self.agreement.id)

    def test_prepare_equipment_values_without_sale(self):
        """No agreement_id when the move is not linked to a sale order."""
        self.order.action_confirm()
        stock_move = self.order.picking_ids.move_ids[:1]
        stock_move.sale_line_id = False
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-NOSALE",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        move_line = self.env["stock.move.line"].create(
            {
                "move_id": stock_move.id,
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "location_id": stock_move.location_id.id,
                "location_dest_id": stock_move.location_dest_id.id,
                "lot_id": lot.id,
                "quantity": 1,
            }
        )
        values = stock_move.prepare_equipment_values(move_line)
        self.assertNotIn("agreement_id", values)
