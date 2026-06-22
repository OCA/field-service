# Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import CommonFsOrderFromPos


class TestPosOrderWithFsmNotInRealTime(CommonFsOrderFromPos):
    def test_create_pos_order_with_fsm_not_in_real_time(self):
        self._start_tour("SaleStockDraftFromPosFsmTour", login="accountman")

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
            self.stage.id,
            "The FSM order should be in new stage",
        )

        self.env["pos.session"].search([], limit=1).close_session_from_ui()

        sale_order = after_orders[0]
        pos_order = sale_order.pos_order_line_ids[0].order_id

        self.assertTrue(
            sale_order.pos_order_line_ids, "The sale order should have POS order lines"
        )
        self.assertTrue(
            pos_order.picking_ids in fsm_order.picking_ids,
            "The FSM order should have the picking of the pos order",
        )

        self.assertTrue(
            fsm_order.picking_ids[0].state == "assigned", "Picking should be assigned"
        )
