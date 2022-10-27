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
        for order in self:
            orders = self.env["fsm.order"]
            orders |= self.env["fsm.order"].search(
                [("sale_line_id", "in", order.order_line.ids)]
            )
            orders |= self.env["fsm.order"].search([("sale_id", "=", order.id)])
            order.fsm_order_ids = orders
            order.fsm_order_count = len(order.fsm_order_ids)

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

    def _prepare_line_fsm_values(self, line):
        """
        Prepare the values to create a new FSM Order from a sale order line.
        """
        self.ensure_one()
        templates = line.product_id.fsm_order_template_id
        vals = self._prepare_fsm_values(
            so_id=self.id,
            sol_id=line.id,
            template_id=templates.id,
            location_id=line.fsm_location_id,
        )
        return vals

    def _prepare_fsm_values(self, **kwargs):
        """
        Prepare the values to create a new FSM Order from a sale order.
        """
        self.ensure_one()
        template_id = kwargs.get("template_id", False)
        template_ids = kwargs.get("template_ids", [template_id])
        location_id = kwargs.get("location_id") or self.fsm_location_id
        templates = self.env["fsm.template"].search([("id", "in", template_ids)])
        note = ""
        hours = 0.0
        categories = self.env["fsm.category"]
        for template in templates:
            note += template.instructions or ""
            hours += template.duration
            categories |= template.category_ids
        return {
            "location_id": location_id.id,
            "location_directions": location_id.direction,
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
                [("sale_id", "=", self.id), ("sale_line_id", "=", False)]
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
            lambda l: l.product_id.field_service_tracking == "sale"
            and not l.fsm_order_id
        )
        new_fsm_orders |= self._field_service_generate_sale_fsm_orders(new_fsm_sale_sol)

        # Create new FSM Order for lines set to FSM Line
        new_fsm_line_sol = self.order_line.filtered(
            lambda l: l.product_id.field_service_tracking == "line"
            and not l.fsm_order_id
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
        msg_fsm_links = ""
        for fsm_order in fsm_orders:
            fsm_order.message_post_with_view(
                "mail.message_origin_link",
                values={"self": fsm_order, "origin": self},
                subtype_id=self.env.ref("mail.mt_note").id,
                author_id=self.env.user.partner_id.id,
            )
            msg_fsm_links += (
                " <a href=# data-oe-model=fsm.order data-oe-id={}>{}</a>,".format(
                    fsm_order.id, fsm_order.name
                )
            )
        so_msg_body = _("""Field Service Order(s) Created:{}""".format(msg_fsm_links))
        self.message_post(body=so_msg_body[:-1])

    def _get_invalid_lines(self):
        """Hook to exclude specific lines which should not have location.
        ex : In some case a product can be sold alon or as an option in configrble product (a product with options).
         in the case that product is sold as option within a configurable product, location is mandatory only on this one.
         We have not to repeat the same location for each option.
        """
        lines_without_location = self.order_line.filtered(
            lambda l: not l.fsm_location_id
            and l.product_id.field_service_tracking != "no"
            and l.display_type not in ("line_section", "line_note")
        )
        return lines_without_location

    def action_confirm(self):
        """On SO confirmation, some lines generate field service orders."""
        lines_without_location = self._get_invalid_lines()
        if lines_without_location:
            lines_without_location_count = len(lines_without_location)
            if not self.fsm_location_id and lines_without_location_count > 0:
                raise ValidationError(
                    _(
                        "FSM Location must be set on sale order\n"
                        "or on the line(s) with field service tracking option\n"
                        "(%s line(s))"
                    )
                    % lines_without_location_count
                )
        result = super(SaleOrder, self).action_confirm()
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
