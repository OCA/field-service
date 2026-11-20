# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class FSMPartialDeliveryWizard(models.TransientModel):
    _name = "fsm.partial.delivery.wizard"
    _description = "FSM Partial Delivery Wizard"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")
    sale_line_ids = fields.One2many(
        "fsm.partial.delivery.line", "wizard_id", string="Sale Order Lines"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        fsm_order_id = self.env.context.get("active_id")
        if not fsm_order_id:
            return res

        fsm_order = self.env["fsm.order"].sudo().browse(fsm_order_id)
        sale_order = fsm_order.sale_id
        if not sale_order:
            return res

        sale_lines = sale_order.order_line.filtered(
            lambda line: line.product_id.product_tmpl_id.field_service_tracking
            == "sale"
            and line.product_id.type in ["product", "consu"]
        )

        line_vals = [
            {
                "sale_line_id": line.id,
                "product_id": line.product_id.id,
                "requested_quantity": line.product_uom_qty,
                "quantity_done": line.qty_delivered,
                "discount": line.discount,
            }
            for line in sale_lines
        ]

        created_lines = self.env["fsm.partial.delivery.line"].create(line_vals)
        res["sale_line_ids"] = [(6, 0, created_lines.ids)]
        res["fsm_order_id"] = fsm_order.id
        return res

    def _update_sale_lines_and_collect_undelivered(self):
        undelivered_lines = []
        original_order = self.fsm_order_id.sale_id
        pricelist = original_order.pricelist_id

        for line in self.sale_line_ids:
            delivered_qty = line.quantity_done
            product = line.product_id

            if line.sale_line_id:
                sale_line = line.sale_line_id

                if (
                    product.product_tmpl_id.create_backorder_sale
                    and delivered_qty < sale_line.product_uom_qty
                ):
                    undelivered_qty = sale_line.product_uom_qty - delivered_qty
                    price_unit = pricelist._get_product_price(product, undelivered_qty)
                    undelivered_lines.append(
                        {
                            "product_id": product.id,
                            "product_uom_qty": undelivered_qty,
                            "product_uom": product.uom_id.id,
                            "price_unit": price_unit,
                            "discount": line.discount,
                            "name": product.display_name,
                        }
                    )

                # qty_delivered is set after action_complete() in
                # action_confirm_partial_delivery to avoid being overwritten
                # by the stage-change triggered recomputation (Odoo 18).
                sale_line.product_uom_qty = delivered_qty
                sale_line.discount = line.discount

            else:
                price_unit = pricelist._get_product_price(product, delivered_qty)
                original_order.write(
                    {
                        "order_line": [
                            (
                                0,
                                0,
                                {
                                    "product_id": product.id,
                                    "product_uom_qty": delivered_qty,
                                    "product_uom": product.uom_id.id,
                                    "price_unit": price_unit,
                                    "discount": line.discount,
                                    "name": product.display_name,
                                },
                            )
                        ]
                    }
                )

        return undelivered_lines

    def _update_sale_line_prices(self):
        for line in self.sale_line_ids:
            sale_line = line.sale_line_id
            order = sale_line.order_id
            pricelist = order.pricelist_id if order else None
            if pricelist:
                price = pricelist._get_product_price(
                    line.product_id, line.quantity_done
                )
                sale_line.price_unit = price
            else:
                sale_line.price_unit = line.product_id.lst_price

    def _create_new_sale_order(self, undelivered_lines):
        original_order = None
        for line in self.sale_line_ids:
            if line.sale_line_id:
                original_order = line.sale_line_id.order_id
                break
        if not original_order:
            original_order = self.fsm_order_id.sale_id
        if not original_order:
            return

        partner = original_order.partner_id
        pricelist = partner.property_product_pricelist or original_order.pricelist_id

        order_lines = []
        for line_vals in undelivered_lines:
            product = self.env["product.product"].browse(line_vals["product_id"])
            qty = line_vals["product_uom_qty"]
            price_unit = line_vals.get("price_unit", 0.0)
            if pricelist:
                price_unit = pricelist._get_product_price(product, qty)
            line_vals["price_unit"] = price_unit
            order_lines.append((0, 0, line_vals))

        new_order_vals = {
            "partner_id": partner.id,
            "fsm_location_id": original_order.fsm_location_id.id,
            "origin": original_order.name,
            "pricelist_id": pricelist.id,
            "order_line": order_lines,
            "payment_term_id": original_order.payment_term_id.id,
        }
        new_order = self.env["sale.order"].sudo().create(new_order_vals)
        new_order.action_confirm()

        original_order.message_post(
            body=_(
                "A new Sale Order <a href='#' data-oe-model='sale.order' "
                "data-oe-id='%(order_id)d'>%(order_name)s</a> was created for "
                "undelivered products."
            )
            % {
                "order_id": new_order.id,
                "order_name": new_order.name,
            }
        )

    def action_confirm_partial_delivery(self):
        undelivered_lines = self._update_sale_lines_and_collect_undelivered()
        self._update_sale_line_prices()

        if undelivered_lines:
            self._create_new_sale_order(undelivered_lines)

        pickings = self.fsm_order_id.sale_id.picking_ids.filtered(
            lambda p: not p.fsm_order_id and p.state not in ("done", "cancel")
        )
        for picking in pickings:
            picking.fsm_order_id = self.fsm_order_id

        self.fsm_order_id.action_complete()
        # Re-apply qty_delivered after action_complete because the FSM stage
        # change triggers recomputation of qty_delivered for stock-move-tracked
        # lines (Odoo 18), which would otherwise reset it to 0.
        for line in self.sale_line_ids:
            if line.sale_line_id:
                line.sale_line_id.qty_delivered = line.quantity_done


class FSMPartialDeliveryLine(models.TransientModel):
    _name = "fsm.partial.delivery.line"
    _description = "FSM Partial Delivery Line"

    wizard_id = fields.Many2one(
        "fsm.partial.delivery.wizard", string="FSM Partial Delivery Wizard"
    )
    sale_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('product_tmpl_id.field_service_tracking', '=', 'sale')]",
    )
    requested_quantity = fields.Float(string="Ordered Quantity")
    quantity_done = fields.Float(string="Quantity Delivered", default=0.0)
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
