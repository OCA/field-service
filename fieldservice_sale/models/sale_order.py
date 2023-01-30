# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fsm_location_id = fields.Many2one(
        "fsm.location",
        string="Service Location",
        help="SO Lines generating a FSM order will be for this location",
        compute="_compute_fsm_location_id",
        precompute=True,
        store=True,
        readonly=False,
    )
    fsm_order_ids = fields.Many2many(
        "fsm.order",
        compute="_compute_fsm_order_ids",
        string="Field Service orders associated to this sale",
    )
    fsm_order_count = fields.Integer(
        string="FSM Orders", compute="_compute_fsm_order_ids"
    )

    @api.depends("order_line")
    def _compute_fsm_order_ids(self):
        for sale in self:
            fsm = self.env["fsm.order"].search(
                [
                    "|",
                    ("sale_id", "=", sale.id),
                    ("sale_line_id", "in", sale.order_line.ids),
                ]
            )
            sale.fsm_order_ids = fsm
            sale.fsm_order_count = len(sale.fsm_order_ids)

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_fsm_location_id(self):
        """
        Autofill the Sale Order's FS location with the partner_id,
        the partner_shipping_id or the partner_id.commercial_partner_id if
        they are FS locations.
        """
        for so in self:
            if so.partner_id.fsm_location:
                domain = [("partner_id", "=", so.partner_id.id)]
            else:
                domain = [
                    "|",
                    "|",
                    ("partner_id", "=", so.partner_id.id),
                    ("partner_id", "=", so.partner_shipping_id.id),
                    ("partner_id", "=", so.partner_id.commercial_partner_id.id),
                ]
            so.fsm_location_id = self.env["fsm.location"].search(domain, limit=1)

    def _field_create_fsm_order_prepare_values(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda sol: sol.product_id.field_service_tracking == "sale"
        )
        templates = lines.product_id.fsm_order_template_id
        note = ""
        hours = 0.0
        categories = self.env["fsm.category"]
        for template in templates:
            note += template.instructions or ""
            hours += template.duration
            categories |= template.category_ids
        return {
            "location_id": self.fsm_location_id.id,
            "location_directions": self.fsm_location_id.direction,
            "request_early": self.expected_date,
            "scheduled_date_start": self.expected_date,
            "todo": note,
            "category_ids": [(6, 0, categories.ids)],
            "scheduled_duration": hours,
            "sale_id": self.id,
            "company_id": self.company_id.id,
        }

    def _field_create_fsm_order(self):
        """Generate fsm_order for the given Sale Order, and link it.
        :return a mapping with the sale order id and its linked fsm_order
        :rtype dict
        """
        result = {}
        for so in self:
            # create fsm_order
            values = so._field_create_fsm_order_prepare_values()
            fsm_order = self.env["fsm.order"].sudo().create(values)
            # post message on SO
            msg_body = _(
                """Field Service Order Created: <a href=
                   # data-oe-model=fsm.order data-oe-id={}>{}</a>
                """
            ).format(fsm_order.id, fsm_order.name)
            so.message_post(body=msg_body)
            # post message on fsm_order
            fsm_order_msg = _(
                """This order has been created from: <a href=
                   # data-oe-model=sale.order data-oe-id={}>{}</a>
                """
            ).format(so.id, so.name)
            fsm_order.message_post(body=fsm_order_msg)
            result[so.id] = fsm_order
        return result

    def _field_find_fsm_order(self):
        """Find the fsm_order generated by the Sale Order. If no fsm_order
        linked, it will be created automatically.
        :return a mapping with the sale order id and its linked fsm_order
        :rtype dict
        """
        fsm_orders = self.env["fsm.order"].search(
            [("sale_id", "in", self.ids), ("sale_line_id", "=", False)]
        )
        result = {f.sale_id.id: f for f in fsm_orders}
        for so in self:
            # If not found, create one fsm_order for the so
            if not result.get(so.id):
                result.update(so._field_create_fsm_order())
        return result

    def _action_confirm(self):
        """On SO confirmation, some lines generate field service orders."""
        result = super()._action_confirm()
        for so in self:
            lines = so.order_line
            if any(sol.product_id.field_service_tracking != "no" for sol in lines):
                if not so.fsm_location_id:
                    raise ValidationError(_("FSM Location must be set"))
                lines._field_service_generation()
        return result

    def action_view_fsm_order(self):
        fsm_orders = self.mapped("fsm_order_ids")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_dash_order"
        )
        if len(fsm_orders) > 1:
            action["domain"] = [("id", "in", fsm_orders.ids)]
        elif len(fsm_orders) == 1:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = fsm_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
