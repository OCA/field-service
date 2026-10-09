# Copyright 2026 Antoni Marroig (APSL-Nagarro) <antoni.marroig@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _is_excluded_from_load_sheet(self):
        """Cancelled orders are not delivered, so they are left out of the
        load sheet of their day route."""
        self.ensure_one()
        cancelled_stage = self.env.ref(
            "fieldservice.fsm_stage_cancelled", raise_if_not_found=False
        )
        return bool(cancelled_stage) and self.stage_id == cancelled_stage

    def _get_load_sheet_moves(self):
        """Return the pending deliveries of the transfers of this order first,
        then its pending pick-ups. Completed orders also return their done
        moves, to show what was delivered and picked up.

        Keep in sync with ``fsm.route.dayroute.product.summary._table_query``.
        """
        self.ensure_one()
        excluded_states = {"draft", "cancel"}
        if not self.is_closed:
            excluded_states.add("done")
        moves = self.sudo().picking_ids.move_ids.filtered(
            lambda move: move.state not in excluded_states
            and (move._is_load_sheet_delivery() or move._is_load_sheet_pickup())
        )
        return moves.sorted(
            lambda move: (move._is_load_sheet_pickup(), move.sequence, move.id)
        )
