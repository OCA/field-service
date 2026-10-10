# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import fields, models
from odoo.tools import float_compare


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        "fsm_order_id",
        string="Timesheets",
    )

    # ------------------------------------------------------------------
    # Sale order
    # ------------------------------------------------------------------
    def _prepare_sale_line_vals(self, product, qty, uom):
        self.ensure_one()
        return {
            "order_id": self.sale_id.id,
            "product_id": product.id,
            "product_uom_qty": qty,
            "product_uom": uom.id,
            "fsm_order_id": self.id,
        }

    # ------------------------------------------------------------------
    # Timesheets -> sale order lines
    # ------------------------------------------------------------------
    def _create_sale_lines_from_timesheets(self):
        self.ensure_one()
        SaleLine = self.env["sale.order.line"]
        lines = self.timesheet_ids.filtered(
            lambda t: t.product_id and not t.fsm_sale_line_id
        )
        grouped = defaultdict(lambda: self.env["account.analytic.line"])
        for line in lines:
            grouped[line.product_id] |= line
        for product, ts_lines in grouped.items():
            uom = product.uom_id
            qty = 0.0
            for ts in ts_lines:
                src_uom = ts.product_uom_id or uom
                if src_uom.category_id == uom.category_id and src_uom != uom:
                    qty += src_uom._compute_quantity(ts.unit_amount, uom)
                else:
                    qty += ts.unit_amount
            if float_compare(qty, 0.0, precision_rounding=uom.rounding) <= 0:
                continue
            vals = self._prepare_sale_line_vals(product, qty, uom)
            # Time has no stock move backing it, so the delivered quantity is
            # set explicitly (these service lines use the manual delivery
            # method).
            vals["qty_delivered"] = qty
            sol = SaleLine.create(vals)
            ts_lines.write({"fsm_sale_line_id": sol.id})

    # ------------------------------------------------------------------
    # Consumed materials (stock moves) -> sale order lines
    # ------------------------------------------------------------------
    @staticmethod
    def _move_qty_in_uom(move, uom):
        """``move.quantity_done`` converted to ``uom`` when compatible."""
        qty = move.quantity_done
        if move.product_uom.category_id == uom.category_id and move.product_uom != uom:
            qty = move.product_uom._compute_quantity(qty, uom)
        return qty

    def _net_move_qty(self, product, moves):
        """Net delivered quantity for ``moves``, expressed in ``product``'s UoM.

        Outgoing moves are materials consumed on site, incoming moves are
        materials returned: they net each other out.
        """
        uom = product.uom_id
        qty = 0.0
        for move in moves:
            sign = 1.0 if move.picking_id.picking_type_id.code == "outgoing" else -1.0
            qty += sign * self._move_qty_in_uom(move, uom)
        return qty

    def _create_sale_lines_from_materials(self):
        self.ensure_one()
        SaleLine = self.env["sale.order.line"]
        moves = self.move_ids.filtered(
            lambda m: m.state == "done" and not m.fsm_sale_line_id
        )
        grouped = defaultdict(lambda: self.env["stock.move"])
        for move in moves:
            grouped[move.product_id] |= move
        for product, prod_moves in grouped.items():
            uom = product.uom_id
            qty = self._net_move_qty(product, prod_moves)
            if float_compare(qty, 0.0, precision_rounding=uom.rounding) <= 0:
                continue
            # The materials have already been delivered through the field
            # service order's own stock moves. Skip the procurement that would
            # otherwise generate a duplicate delivery on the sale order, and
            # link those moves to the new line so its delivered quantity is
            # computed from them natively (stock move delivery method).
            sol = SaleLine.with_context(skip_procurement=True).create(
                self._prepare_sale_line_vals(product, qty, uom)
            )
            prod_moves.write({"sale_line_id": sol.id, "fsm_sale_line_id": sol.id})

    # ------------------------------------------------------------------
    # Action
    # ------------------------------------------------------------------
    def action_create_sale_lines(self):
        """Push the recorded timesheets and consumed materials to the order's
        sale order for invoicing.

        The field service order must already be linked to a sale order (it was
        generated from one); this never creates a sale order. Orders without a
        sale order are skipped, and the button is hidden for them.
        """
        for order in self.filtered("sale_id"):
            order._create_sale_lines_from_timesheets()
            order._create_sale_lines_from_materials()
        if len(self) == 1:
            return self.action_view_sales()
        return True

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    def _report_material_lines(self):
        """Consumed and returned materials for the printed report.

        Returns a list of ``{"product", "direction", "qty", "uom"}`` dicts,
        one row per product and direction, where ``direction`` is ``"out"``
        (materials used on site) or ``"in"`` (materials returned). Quantities
        are summed per group and expressed in the product's UoM; returns are
        listed on their own rows rather than netted against the consumption,
        so the report shows both what went out and what came back. Rows are
        ordered by product, used before returned.
        """
        self.ensure_one()
        grouped = defaultdict(lambda: self.env["stock.move"])
        for move in self.move_ids.filtered(lambda m: m.state == "done"):
            direction = (
                "out" if move.picking_id.picking_type_id.code == "outgoing" else "in"
            )
            grouped[(move.product_id, direction)] |= move
        lines = []
        for (product, direction), moves in grouped.items():
            uom = product.uom_id
            qty = sum(self._move_qty_in_uom(move, uom) for move in moves)
            if float_compare(qty, 0.0, precision_rounding=uom.rounding) <= 0:
                continue
            lines.append(
                {
                    "product": product,
                    "direction": direction,
                    "qty": qty,
                    "uom": uom,
                }
            )
        lines.sort(
            key=lambda line: (
                line["product"].display_name,
                0 if line["direction"] == "out" else 1,
            )
        )
        return lines
