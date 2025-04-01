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

    def _prepare_line_fsm_values(self, line):
        """
        Prepare the values to create a new FSM Order from a sale order line.
        """
        self.ensure_one()
        templates = line.product_id.fsm_order_template_id
        vals = self._prepare_fsm_values(
            so_id=self.id, sol_id=line.id, template_id=templates.id
        )
        return vals

    def _prepare_fsm_values(self, **kwargs):
        """
        Prepare the values to create a new FSM Order from a sale order.
        """
        self.ensure_one()
        template_id = kwargs.get("template_id", False)
        template_ids = kwargs.get("template_ids", [template_id])
        templates = self.env["fsm.template"].search([("id", "in", template_ids)])
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
            "sale_id": kwargs.get("so_id", False),
            "sale_line_id": kwargs.get("sol_id", False),
            "template_id": template_id,
            "company_id": self.company_id.id,
        }

    def _field_service_generate_sale_fsm_orders(self, new_fsm_sol):
        """
        Generate the FSM Order for this sale order if it doesn't exist.
        """
        self.ensure_one()
        new_fsm_orders = self.env["fsm.order"]

        if new_fsm_sol:
            fsm_by_sale = self.env["fsm.order"].search(
                [
                    ("sale_id", "=", self.id),
                    ("sale_line_id", "=", False),
                    ("is_closed", "=", False),
                ]
            )
            if not fsm_by_sale:
                templates = new_fsm_sol.product_id.fsm_order_template_id
                vals = self._prepare_fsm_values(
                    so_id=self.id, template_ids=templates.ids
                )
                fsm_by_sale = self.env["fsm.order"].sudo().create(vals)
                new_fsm_orders |= fsm_by_sale
            new_fsm_sol.write({"fsm_order_id": fsm_by_sale.id})

        return new_fsm_orders

    def _field_service_generate_line_fsm_orders(self, new_fsm_sol):
        """
        Generate FSM Orders for the given sale order lines.

        Override this method to filter lines to generate FSM Orders for.
        """
        self.ensure_one()
        new_fsm_orders = self.env["fsm.order"]

        for line in new_fsm_sol:
            vals = self._prepare_line_fsm_values(line)
            fsm_by_line = self.env["fsm.order"].sudo().create(vals)
            line.write({"fsm_order_id": fsm_by_line.id})
            new_fsm_orders |= fsm_by_line

        return new_fsm_orders

    def _field_service_generate(self):
        """
        Generate FSM Orders for this sale order.

        Override this method to add new field_service_tracking types.
        """
        self.ensure_one()
        new_fsm_orders = self.env["fsm.order"]

        # Process lines set to FSM Sale
        new_fsm_sale_sol = self.order_line.filtered(
            lambda x: x.product_id.field_service_tracking == "sale"
            and (not x.fsm_order_id or x.fsm_order_id.is_closed)
        )
        new_fsm_orders |= self._field_service_generate_sale_fsm_orders(new_fsm_sale_sol)

        # Create new FSM Order for lines set to FSM Line
        new_fsm_line_sol = self.order_line.filtered(
            lambda x: x.product_id.field_service_tracking == "line"
            and (not x.fsm_order_id or x.fsm_order_id.is_closed)
        )

        new_fsm_orders |= self._field_service_generate_line_fsm_orders(new_fsm_line_sol)

        return new_fsm_orders

    def _field_service_generation(self):
        """
        Create Field Service Orders based on the products' configuration.
        :rtype: list(FSM Orders)
        :return: list of newly created FSM Orders
        """
        created_fsm_orders = self.env["fsm.order"]

        for sale in self:
            new_fsm_orders = self._field_service_generate()

            if len(new_fsm_orders) > 0:
                created_fsm_orders |= new_fsm_orders
                # If FSM Orders were created, post a message to the Sale Order
                sale._post_fsm_message(new_fsm_orders)

        return created_fsm_orders

    def _post_fsm_message(self, fsm_orders):
        """
        Post messages to the Sale Order and the newly created FSM Orders
        """
        self.ensure_one()
        for fsm_order in fsm_orders:
            fsm_order.message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": fsm_order, "origin": self},
                subtype_xmlid="mail.mt_note",
            )
        so_msg_body = _(
            "Field Service Order(s) Created: %s",
            fsm_order._get_html_link(title=fsm_order.name),
        )
        self.message_post(body=so_msg_body[:-1])

    def _action_confirm(self):
        """On SO confirmation, some lines generate field service orders."""
        result = super()._action_confirm()
        if any(
            sol.product_id.field_service_tracking != "no"
            for sol in self.order_line.filtered(
                lambda x: x.display_type not in ("line_section", "line_note")
            )
        ):
            if not self.fsm_location_id:
                raise ValidationError(_("FSM Location must be set"))
            self._field_service_generation()
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

    def _action_cancel(self):
        res = super()._action_cancel()

        [fsm_order.action_cancel() for fsm_order in self.mapped("fsm_order_ids")]

        return res
