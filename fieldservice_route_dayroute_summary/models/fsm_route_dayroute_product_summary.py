# Copyright 2026 Antoni Marroig (APSL-Nagarro) <antoni.marroig@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRouteProductSummary(models.Model):
    _name = "fsm.route.dayroute.product.summary"
    _description = "Day Route Product To Load"
    _auto = False
    _rec_name = "product_id"
    _order = "dayroute_id, product_id"
    # Fields the query reads, flushed before querying the model
    _depends = {
        "fsm.order": ["dayroute_id", "stage_id"],
        "stock.move": [
            "picking_id",
            "location_id",
            "location_dest_id",
            "state",
            "product_id",
            "product_uom",
            "product_qty",
            "quantity",
        ],
        "stock.picking": ["fsm_order_id"],
        "stock.location": ["usage"],
        "product.product": ["product_tmpl_id", "weight"],
        "product.template": ["uom_id"],
        "uom.uom": ["factor"],
    }

    dayroute_id = fields.Many2one(
        "fsm.route.dayroute", string="Day Route", readonly=True
    )
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    quantity = fields.Float(digits="Product Unit of Measure", readonly=True)
    reserved_quantity = fields.Float(
        string="Reserved", digits="Product Unit of Measure", readonly=True
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", readonly=True)
    weight = fields.Float(digits="Stock Weight", readonly=True)
    weight_uom_name = fields.Char(
        string="Weight Unit", compute="_compute_weight_uom_name"
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        # Display the weight unit in the label, as it is not the same for all
        # databases: "Weight (kg)"
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if res.get("weight", {}).get("string"):
            weight_uom_name = self.env[
                "product.template"
            ]._get_weight_uom_name_from_ir_config_parameter()
            res["weight"]["string"] = f"{res['weight']['string']} ({weight_uom_name})"
        return res

    def _compute_weight_uom_name(self):
        weight_uom_name = self.env[
            "product.template"
        ]._get_weight_uom_name_from_ir_config_parameter()
        for line in self:
            line.weight_uom_name = weight_uom_name

    @property
    def _table_query(self):
        """Quantities to deliver per product of each day route, and how much of
        them is reserved, in the product unit of measure. Only the pending
        deliveries of the orders count (moves to the customer), pick-ups are
        left out.

        Keep in sync with ``fsm.order._get_load_sheet_moves`` and
        ``stock.move._is_load_sheet_delivery``.
        """
        cancelled_stage = self.env.ref(
            "fieldservice.fsm_stage_cancelled", raise_if_not_found=False
        )
        return f"""
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY fo.dayroute_id, sm.product_id
                ) AS id,
                fo.dayroute_id AS dayroute_id,
                sm.product_id AS product_id,
                pt.uom_id AS uom_id,
                SUM(sm.product_qty) AS quantity,
                SUM(
                    sm.quantity / move_uom.factor * product_uom.factor
                ) AS reserved_quantity,
                SUM(sm.product_qty * COALESCE(pp.weight, 0.0)) AS weight
            FROM stock_move sm
            JOIN stock_picking sp ON sp.id = sm.picking_id
            JOIN fsm_order fo ON fo.id = sp.fsm_order_id
            JOIN stock_location src ON src.id = sm.location_id
            JOIN stock_location dst ON dst.id = sm.location_dest_id
            JOIN product_product pp ON pp.id = sm.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN uom_uom move_uom ON move_uom.id = sm.product_uom
            JOIN uom_uom product_uom ON product_uom.id = pt.uom_id
            WHERE fo.dayroute_id IS NOT NULL
                AND fo.stage_id IS DISTINCT FROM {int(cancelled_stage.id or 0)}
                AND dst.usage = 'customer'
                AND src.usage != 'customer'
                AND sm.state NOT IN ('draft', 'cancel', 'done')
            GROUP BY fo.dayroute_id, sm.product_id, pt.uom_id
        """
