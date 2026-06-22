# Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from itertools import groupby

from odoo import _, models
from odoo.tools.float_utils import float_compare, float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_move_from_pos_order_lines(self, lines):
        """
        Create picking for POS orders with FSM products.
        Handles:
        1. Non-real-time stock updates: Creates pickings.
        2. Real-time stock updates: Creates stock moves directly.
        3. Refunds: Adjusts stock moves and cancels pickings if necessary.
        """
        self.ensure_one()

        orders_dict = defaultdict(list)
        for line in lines:
            orders_dict[line.order_id.id].append(line)

        processed_lines = set()

        for order_lines in orders_dict.values():
            pos_order = order_lines[0].order_id
            sale_order = order_lines[0].sale_order_origin_id if order_lines else None
            has_fsm_products = any(
                line.product_id.field_service_tracking != "no"
                for line in pos_order.lines
            )

            if self._is_refund(pos_order, order_lines):
                self._handle_refund(pos_order, order_lines, processed_lines)
                continue

            if has_fsm_products and sale_order:
                if not pos_order._should_create_picking_real_time():
                    self._create_fsm_picking(pos_order, order_lines, sale_order)
                else:
                    self._create_fsm_moves(order_lines, sale_order)
                processed_lines.update(order_lines)

        remaining_lines = [line for line in lines if line not in processed_lines]
        if remaining_lines:
            return super()._create_move_from_pos_order_lines(remaining_lines)

        return None

    def _handle_refund(self, pos_order, order_lines, processed_lines):
        """
        Handle FSM refunds by adjusting pickings or stock moves directly.
        """
        pickings = pos_order.refunded_order_ids.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel") and p.fsm_order_id
        )
        # Check if there are not more FSM products in the picking
        # So we can cancel the FSM order and confirm the picking
        self._check_no_fsm_products(pickings, order_lines)
        refunded_pickings = pos_order.refunded_order_ids.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel") and p.fsm_order_id
        )
        refunded_lines = self._process_refund(order_lines, refunded_pickings)
        return processed_lines.update(refunded_lines)

    def _process_refund(self, order_lines, refunded_pickings):
        """
        Adjust stock move quantities for refunded lines if FSM order is still active.
        Cancel picking and FSM order if no moves remain.
        """
        processed_lines = set()

        if not refunded_pickings:
            return processed_lines

        completed_stage = self.env.ref("fieldservice.fsm_stage_completed")

        for picking in refunded_pickings:
            fsm_order = picking.fsm_order_id
            if not fsm_order or fsm_order.stage_id == completed_stage:
                continue
            moves_to_unlink = []
            for stock_move in picking.move_ids:
                for line in order_lines:
                    if line.product_id.id == stock_move.product_id.id:
                        stock_move.product_uom_qty += line.qty
                        stock_move.quantity = stock_move.product_uom_qty
                        if (
                            float_compare(
                                stock_move.product_uom_qty,
                                0.0,
                                precision_rounding=stock_move.product_uom.rounding,
                            )
                            <= 0
                        ):
                            moves_to_unlink.append(stock_move)
                        processed_lines.add(line)

            for move in moves_to_unlink:
                move.unlink()

            moves_with_qty = picking.move_ids.filtered(
                lambda m: not float_is_zero(
                    m.product_uom_qty, precision_rounding=m.product_uom.rounding
                )
            )
            if not moves_with_qty:
                picking.action_cancel()
                fsm_order.action_cancel()
                self._post_fsm_message(order_lines[0].order_id, fsm_order)

        return processed_lines

    def _check_no_fsm_products(self, refunded_pickings, order_lines):
        completed_stage = self.env.ref("fieldservice.fsm_stage_completed")
        for picking in refunded_pickings:
            fsm_order = picking.fsm_order_id
            if not fsm_order or fsm_order.stage_id == completed_stage:
                continue

            fsm_product_ids = picking.move_ids.filtered(
                lambda m: m.product_id.field_service_tracking != "no"
            ).mapped("product_id.id")

            refunded_fsm_lines = [
                line
                for line in order_lines
                if line.product_id.id in fsm_product_ids and line.qty < 0
            ]

            refunded_ids = {line.product_id.id for line in refunded_fsm_lines}

            # If all FSM products in the picking are refunded
            # and no other FSM products remain
            # we can cancel the FSM order and confirm the picking
            if set(fsm_product_ids).issubset(refunded_ids):
                if picking.state not in ("done", "cancel"):
                    picking.button_validate()
                if fsm_order.stage_id != completed_stage:
                    fsm_order.picking_ids = False
                    fsm_order.action_cancel()
                    self._post_fsm_message(order_lines[0].order_id, fsm_order)
                continue

    def _post_fsm_message(self, pos_order, fsm_order):
        if fsm_order:
            fsm_order.message_post(
                body=(
                    _(
                        f"FSM Order automatically canceled due to full refund. "
                        f"From {pos_order.name}."
                    )
                ),
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )

    def _create_fsm_picking(self, pos_order, order_lines, sale_order):
        """
        Create a stock picking linked to FSM order for the given POS order.
        """
        fsm_order = self._get_fsm_order_from_sale_order(sale_order)
        picking = self.env["stock.picking"].create(
            {
                "partner_id": pos_order.partner_id.id,
                "origin": pos_order.name,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "picking_type_id": self.picking_type_id.id,
                "pos_order_id": pos_order.id,
                "company_id": pos_order.company_id.id,
                "fsm_order_id": fsm_order.id if fsm_order else False,
            }
        )

        for line in order_lines:
            if line.product_id.type == "service":
                continue
            self.env["stock.move"].create(
                {
                    "name": line.product_id.name,
                    "picking_id": picking.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                    "quantity": line.qty,
                    "product_uom": line.product_id.uom_id.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "company_id": pos_order.company_id.id,
                    "fsm_order_id": fsm_order.id if fsm_order else False,
                }
            )
        picking.action_assign()

    def _create_fsm_moves(self, order_lines, sale_order):
        """
        Directly create stock moves for real-time FSM stock updates.
        """
        fsm_order = self._get_fsm_order_from_sale_order(sale_order)
        lines_by_product = groupby(
            sorted(order_lines, key=lambda line: line.product_id.id),
            key=lambda line: line.product_id.id,
        )

        move_vals = []
        for __, grouped_lines in lines_by_product:
            pos_order_lines = self.env["pos.order.line"].concat(*grouped_lines)
            vals = self._prepare_stock_move_vals(pos_order_lines[0], pos_order_lines)
            vals["fsm_order_id"] = fsm_order.id if fsm_order else False
            move_vals.append(vals)

        if fsm_order.picking_ids:
            fsm_order.picking_ids[0].action_cancel()

        moves = self.env["stock.move"].create(move_vals)
        moves._add_mls_related_to_order(pos_order_lines, are_qties_done=True)
        self._link_owner_on_return_picking(pos_order_lines)
        moves[0].picking_id.fsm_order_id = fsm_order

    def _is_refund(self, pos_order, order_lines):
        """
        Check if the order has refunded lines.
        """
        return pos_order.refunded_order_ids and any(
            line.qty < 0 for line in order_lines
        )

    def _get_fsm_order_from_sale_order(self, sale_order):
        """
        Find the FSM order linked to a sale order.
        """
        return self.env["fsm.order"].search([("sale_id", "=", sale_order.id)], limit=1)
