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
        for rec in self:
            orders = self.env["fsm.order"].search(
                [("sale_line_ids", "in", rec.order_line.ids)]
            )
            rec.fsm_order_ids = orders
            rec.fsm_order_count = len(rec.fsm_order_ids)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Autofill the Sale Order's FS location with the partner_id,
        the partner_shipping_id or the partner_id.commercial_partner_id if
        they are FS locations.
        """
        super(SaleOrder, self).onchange_partner_id()
        domain = [
            "|",
            "|",
            ("partner_id", "=", self.partner_id.id),
            ("partner_id", "=", self.partner_shipping_id.id),
            ("partner_id", "=", self.partner_id.commercial_partner_id.id),
        ]
        if self.partner_id.fsm_location:
            domain = [("partner_id", "=", self.partner_id.id)]
        location_ids = self.env["fsm.location"].search(domain)
        self.fsm_location_id = location_ids and location_ids[0] or False

    def _prepare_fsm_values(self, template=False):
        self.ensure_one()
        if template:
            note = template.instructions
            categories = template.category_ids
            hours = template.duration
        return {
            "location_id": self.fsm_location_id.id,
            "location_directions": self.fsm_location_id.direction,
            "request_early": self.expected_date,
            "scheduled_date_start": self.expected_date,
            "template_id": template.id or False,
            "todo": note or "",
            "category_ids": [(6, 0, categories.ids)] or False,
            "scheduled_duration": hours or 0.0,
            "company_id": self.company_id.id,
        }

    def _field_service_generation(self):
        """
        Create Field Service Orders based on the products' configuration.

        :rtype: list(integer)
        :return: ids of newly created FSM Orders
        """
        res = []
        for order in self:
            to_create = order._split_fsm_lines()
            for (template, order_lines) in to_create:
                values = order._prepare_fsm_values(template)
                fsm_order = self.env["fsm.order"].sudo().create(values)
                order_lines.write({"fsm_order_id": fsm_order.id})
                res.append(fsm_order.id)
                fsm_order.message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": fsm_order, "origin": order},
                    subtype_id=self.env.ref("mail.mt_note").id,
                    author_id=self.env.user.partner_id.id,
                )
        return res

    def _split_fsm_lines(self):
        """
        Split the sale order lines according to the field service templates that
        need to be created.

        Products with Field Service Tracking set to:
         - Sale: Create one FSM order for like FSM templates
         - SO Line: Create one FSM order for every line regardless of FSM template

        :rtype: list(tuple)
        :return: [(template_id, order_line_ids), ...]
        """
        self.ensure_one()
        res = []
        new_fsm_lines = self.order_line.filtered(
            lambda l: not l.fsm_order_id
            and not l.product_id.field_service_tracking == "no"
        )
        fsm_by_sale = new_fsm_lines.filtered(
            lambda l: l.product_id.field_service_tracking == "sale"
        )
        templates = fsm_by_sale.mapped("product_id.fsm_order_template_id")
        for template in templates:
            lines = fsm_by_sale.filtered(
                lambda l: l.product_id.fsm_order_template_id == template
            )
            res.append((template, lines))
        fsm_by_line = new_fsm_lines.filtered(
            lambda l: l.product_id.field_service_tracking == "line"
        )
        for line in fsm_by_line:
            res.append((line.product_id.fsm_order_template_id, line))
        return res

    def _action_confirm(self):
        """ On SO confirmation, some lines generate field service orders. """
        result = super(SaleOrder, self)._action_confirm()
        if any(
            sol.product_id.field_service_tracking != "no" for sol in self.order_line
        ):
            if not self.fsm_location_id:
                raise ValidationError(_("FSM Location must be set"))
            self._field_service_generation()
        return result

    def action_view_fsm_order(self):
        fsm_orders = self.mapped("fsm_order_ids")
        action = self.env.ref("fieldservice.action_fsm_dash_order").read()[0]
        if len(fsm_orders) > 1:
            action["domain"] = [("id", "in", fsm_orders.ids)]
        elif len(fsm_orders) == 1:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = fsm_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
