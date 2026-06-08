# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    outgoing_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Outgoing Operation Type",
        domain="[('code', '=', 'outgoing')]",
        compute="_compute_picking_type_ids",
        store=True,
        readonly=False,
        help="Operation type used to create the transfer that sends "
        "materials out to the field service location.",
    )
    incoming_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Incoming Operation Type",
        domain="[('code', '=', 'incoming')]",
        compute="_compute_picking_type_ids",
        store=True,
        readonly=False,
        help="Operation type used to create the transfer that receives "
        "materials back from the field service location.",
    )
    outgoing_line_ids = fields.One2many(
        "fsm.order.stock.line",
        "fsm_order_id",
        string="Outgoing Products",
        domain=[("direction", "=", "outgoing")],
        context={"default_direction": "outgoing"},
    )
    incoming_line_ids = fields.One2many(
        "fsm.order.stock.line",
        "fsm_order_id",
        string="Incoming Products",
        domain=[("direction", "=", "incoming")],
        context={"default_direction": "incoming"},
    )

    @api.depends("warehouse_id", "template_id")
    def _compute_picking_type_ids(self):
        for order in self:
            template = order.template_id
            # A preset on the template wins over the warehouse default; the
            # warehouse default only fills the gap when nothing is set yet.
            if template.outgoing_picking_type_id:
                order.outgoing_picking_type_id = template.outgoing_picking_type_id
            elif not order.outgoing_picking_type_id:
                order.outgoing_picking_type_id = order.warehouse_id.out_type_id
            if template.incoming_picking_type_id:
                order.incoming_picking_type_id = template.incoming_picking_type_id
            elif not order.incoming_picking_type_id:
                order.incoming_picking_type_id = order.warehouse_id.in_type_id

    def _fsm_get_procurement_group(self):
        """Return (creating if needed) the procurement group that links the
        stock transfers to this FSM order. The link relies on the
        ``stock.picking.fsm_order_id`` related field provided by
        ``fieldservice_stock`` (``group_id.fsm_order_id``)."""
        self.ensure_one()
        if not self.procurement_group_id:
            self.procurement_group_id = self.env["procurement.group"].create(
                {
                    "name": self.name,
                    "fsm_order_id": self.id,
                    "move_type": "direct",
                }
            )
        return self.procurement_group_id

    def _get_transfer_locations(self, direction, picking_type):
        """Source and destination locations for a transfer in the given
        direction. The field service side is the inventory (customer) location
        of the order's location; the warehouse side comes from the operation
        type (falling back to the warehouse stock location)."""
        self.ensure_one()
        customer_location = self.location_id.inventory_location_id
        stock_location = self.warehouse_id.lot_stock_id
        if direction == "outgoing":
            location_id = picking_type.default_location_src_id or stock_location
            location_dest_id = (
                customer_location or picking_type.default_location_dest_id
            )
        else:
            location_id = customer_location or picking_type.default_location_src_id
            location_dest_id = picking_type.default_location_dest_id or stock_location
        return location_id, location_dest_id

    def _prepare_transfer_values(
        self, picking_type, location_id, location_dest_id, group
    ):
        """Values for the stock.picking that groups the material moves."""
        self.ensure_one()
        partner = self.location_id.shipping_address_id or self.location_id.partner_id
        return {
            "picking_type_id": picking_type.id,
            "partner_id": partner.id,
            "origin": self.name,
            "location_id": location_id.id,
            "location_dest_id": location_dest_id.id,
            "group_id": group.id,
            "company_id": self.company_id.id,
        }

    def _create_transfer(self, direction):
        """Create a transfer for the material lines of the given direction that
        are not yet linked to an active move. Returns the created picking (or an
        empty recordset when nothing has to be transferred)."""
        self.ensure_one()
        lines = (
            self.outgoing_line_ids
            if direction == "outgoing"
            else self.incoming_line_ids
        ).filtered(lambda line: not line.move_id or line.move_id.state == "cancel")
        if not lines:
            return self.env["stock.picking"]
        picking_type = (
            self.outgoing_picking_type_id
            if direction == "outgoing"
            else self.incoming_picking_type_id
        )
        if not picking_type:
            label = _("outgoing") if direction == "outgoing" else _("incoming")
            raise UserError(
                _(
                    "Please set the %s operation type on the "
                    "field service order before creating transfers."
                )
                % label
            )
        location_id, location_dest_id = self._get_transfer_locations(
            direction, picking_type
        )
        group = self._fsm_get_procurement_group()
        picking = self.env["stock.picking"].create(
            self._prepare_transfer_values(
                picking_type, location_id, location_dest_id, group
            )
        )
        for line in lines:
            move = self.env["stock.move"].create(
                line._prepare_stock_move_values(
                    picking, location_id, location_dest_id, group
                )
            )
            line.move_id = move.id
        return picking

    def action_create_transfers(self):
        """Create the outgoing and/or incoming transfers required by the
        material lines and open them. The pickings are left in draft so the
        user processes them through the standard transfer flow."""
        pickings = self.env["stock.picking"]
        for order in self:
            pickings |= order._create_transfer("outgoing")
            pickings |= order._create_transfer("incoming")
        if not pickings:
            raise UserError(
                _(
                    "There is nothing to transfer. Add outgoing or incoming "
                    "products that are not part of a transfer yet."
                )
            )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        if len(pickings) == 1:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = pickings.id
        else:
            action["domain"] = [("id", "in", pickings.ids)]
        return action
