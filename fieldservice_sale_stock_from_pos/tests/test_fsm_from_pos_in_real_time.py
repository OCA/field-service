# Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import CommonFsOrderFromPos


class TestPosOrderWithFsmInRealTime(CommonFsOrderFromPos):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.point_of_sale_update_stock_quantities = "real"

    def test_create_pos_order_with_fsm_in_real_time(self):
        self._start_tour("PosOrderToSaleOrderTour", login="accountman")

        after_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )

        self.assertTrue(
            after_orders[0].fsm_order_ids, "The sale order should have a FSM order"
        )
        fsm_order = after_orders[0].fsm_order_ids[0]
        self.assertEqual(
            fsm_order.stage_id.id,
            self.completed_stage.id,
            "The FSM order should be in Completed state",
        )
        self.assertTrue(
            fsm_order.picking_ids[0].state == "done", "Picking should be done"
        )

    def test_partial_refund_pos_order_with_fsm_in_real_time(self):
        """Refunds the fsm product"""
        self._start_tour("SaleStockPartialRefundFromPosFsmTour", login="accountman")
        after_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )
        pos_order = after_orders[0].pos_order_line_ids[0].order_id
        session = pos_order.session_id
        pos_order = session.order_ids[1]
        self.assertTrue(
            pos_order.refund_orders_count, "The pos order should have a refunded order"
        )
        self.assertTrue(pos_order.picking_ids.state == "done", "Picking should be done")
        self.assertEqual(
            len(pos_order.picking_ids[0].move_ids),
            2,
        )

        fsm_order = after_orders[0].fsm_order_ids[0]
        self.assertEqual(
            fsm_order.stage_id.id,
            self.cancelled_stage.id,
            "The FSM order should be cancelled after all fsm products refunded",
        )

        self.assertFalse(
            fsm_order.picking_ids,
        )

    def test_full_refund_pos_order_with_fsm_in_real_time(self):
        self._start_tour("SaleStockFullRefundFromPosFsmTour", login="accountman")
        after_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )
        pos_order = after_orders[0].pos_order_line_ids[0].order_id
        session = pos_order.session_id
        pos_order = session.order_ids[1]
        self.assertTrue(
            pos_order.refund_orders_count, "The pos order should have a refunded order"
        )
        self.assertTrue(
            pos_order.picking_ids[0].state == "done",
            "Picking should be done",
        )
        fsm_order = after_orders[0].fsm_order_ids[0]
        self.assertEqual(
            fsm_order.stage_id.id,
            self.cancelled_stage.id,
            "The FSM order should be in cancelled stage",
        )

        self.assertFalse(
            fsm_order.picking_ids,
        )

    def test_create_pos_order_without_fsm(self):
        self.white_board_product.field_service_tracking = False
        self._start_tour("PosOrderToSaleOrderTour", login="accountman")

        after_orders = self.env["sale.order"].search(
            [("partner_id", "=", self.env.ref("base.res_partner_address_31").id)],
            order="id",
        )

        self.assertFalse(
            after_orders[0].fsm_order_ids, "The sale order shouldn't have a FSM order"
        )
