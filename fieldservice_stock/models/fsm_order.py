# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id
        warehouse_ids = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        return warehouse_ids and warehouse_ids.id

    @api.model
    def _get_move_domain(self):
        return [("picking_id.picking_type_id.code", "in", ("outgoing", "incoming"))]

    picking_ids = fields.One2many("stock.picking", "fsm_order_id", string="Transfers")
    delivery_count = fields.Integer(
        string="Delivery Orders", compute="_compute_picking_ids"
    )
    # procurement_group_id field removed: procurement.group model doesn't exist in Odoo 19
    inventory_location_id = fields.Many2one(
        related="location_id.inventory_location_id",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=_default_warehouse_id,
        help="Warehouse used to ship the materials",
    )
    return_count = fields.Integer(
        string="Return Orders", compute="_compute_picking_ids"
    )
    move_ids = fields.One2many(
        "stock.move", "fsm_order_id", string="Operations"
    )

    def action_consume_materials(self):
        """
        Finalize draft stock moves created manually on the FSM order.
        """
        for order in self:
            draft_moves = order.move_ids.filtered(lambda m: m.state == 'draft')
            if not draft_moves:
                continue

            for move in draft_moves:
                if not move.location_id:
                    move.location_id = order.warehouse_id.lot_stock_id.id
                if not move.location_dest_id:
                    move.location_dest_id = order.inventory_location_id.id or order.partner_id.property_stock_customer.id

                if not move.product_uom:
                    move.product_uom = move.product_id.uom_id.id

            draft_moves._action_confirm()
            draft_moves._action_assign()
            draft_moves.picked = True
            draft_moves._action_done()
        return True

    @api.depends("picking_ids")
    def _compute_picking_ids(self):
        for order in self:
            outgoing_pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "outgoing"
            )
            order.delivery_count = len(outgoing_pickings.ids)
            incoming_pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "incoming"
            )
            order.return_count = len(incoming_pickings.ids)

    def action_view_delivery(self):
        """
        This function returns an action that display existing delivery orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        delivery_ids = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        ).ids
        if len(delivery_ids) > 1:
            action["domain"] = [("id", "in", delivery_ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = delivery_ids[0]
        return action

    def action_view_returns(self):
        """
        This function returns an action that display existing return orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one return order to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        return_ids = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        ).ids
        if len(return_ids) > 1:
            action["domain"] = [("id", "in", return_ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = return_ids[0]
        return action
