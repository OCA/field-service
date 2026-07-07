# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FsmOrder(models.Model):
    _inherit = "fsm.order"

    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="fsm_order_id",
        string="Subcontract POs",
        help="Purchase Order auto-created when this FSO was assigned "
        "to a subcontractor worker.",
    )

    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count",
    )

    reassign_worker = fields.Boolean(
        compute="_compute_reassign_worker",
        help="Determine if a worker reassignment can be performed.",
    )

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    @api.depends("purchase_order_ids", "stage_id.is_closed")
    def _compute_reassign_worker(self):
        for order in self:
            order.reassign_worker = order._can_reassign_subcontract_worker()

    def write(self, vals):
        if "person_id" in vals and not self.env.context.get("skip_reassign_check"):
            protected_orders = self.filtered("purchase_order_ids")
            if protected_orders:
                raise UserError(
                    self.env._(
                        "You cannot directly reassign an order with a "
                        "subcontract Purchase Order. Use the Reassign Worker "
                        "button instead."
                    )
                )
        scheduled_fields = {
            "scheduled_date_end",
            "scheduled_duration",
            "scheduled_date_start",
        }
        update_purchase_dates = bool(scheduled_fields.intersection(vals))
        res = super().write(vals)
        if update_purchase_dates:
            self._update_subcontract_po_date_planned()
        return res

    def action_view_purchase_order(self):
        """Smart button action to open linked Purchase Orders."""
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("id", "in", self.purchase_order_ids.ids)],
            "target": "current",
        }
        if len(self.purchase_order_ids) == 1:
            action.update(
                {
                    "res_id": self.purchase_order_ids.id,
                    "view_mode": "form",
                }
            )
        return action

    def action_open_reassign_confirm(self):
        """Open the reassignment confirmation wizard."""
        self.ensure_one()
        self._check_reassign_subcontract_worker_allowed()
        return {
            "type": "ir.actions.act_window",
            "name": _("Confirm Worker Reassignment"),
            "res_model": "fsm.order.reassign.confirm",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_fsm_order_id": self.id,
            },
        }

    def action_cancel(self):
        """Ask how to handle active subcontract POs before cancelling the FSO."""
        if not self.env.context.get("skip_subcontract_cancel_wizard"):
            orders_with_purchase = self.filtered(
                lambda order: order._get_active_subcontract_purchase_orders()
            )
            if orders_with_purchase:
                if len(self) > 1:
                    raise UserError(
                        self.env._(
                            "Cancel Field Service Orders with active subcontract "
                            "Purchase Orders one at a time."
                        )
                    )
                return {
                    "type": "ir.actions.act_window",
                    "name": self.env._("Cancel Field Service Order"),
                    "res_model": "fsm.order.cancel.confirm",
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                        "default_fsm_order_id": orders_with_purchase.id,
                    },
                }
        return super().action_cancel()

    def _can_reassign_subcontract_worker(self):
        self.ensure_one()
        return bool(self.purchase_order_ids) and not self.stage_id.is_closed

    def _check_reassign_subcontract_worker_allowed(self):
        self.ensure_one()
        if self.stage_id.is_closed:
            raise UserError(
                self.env._(
                    "You cannot reassign the worker because the Field Service "
                    "Order is in a closed stage."
                )
            )
        if not self.purchase_order_ids:
            raise UserError(self.env._("There is no subcontract Purchase Order."))

    def _get_active_subcontract_purchase_orders(self):
        return self.purchase_order_ids.filtered(lambda po: po.state != "cancel")

    def _get_posted_subcontract_vendor_bills(self):
        return self._get_active_subcontract_purchase_orders().invoice_ids.filtered(
            lambda invoice: invoice.state == "posted"
        )

    def _get_draft_subcontract_vendor_bills(self):
        return self._get_active_subcontract_purchase_orders().invoice_ids.filtered(
            lambda invoice: invoice.state == "draft"
        )

    def _check_subcontract_purchase_orders_can_be_cancelled(self):
        posted_bills = self._get_posted_subcontract_vendor_bills()
        if posted_bills:
            raise UserError(
                self.env._(
                    "Cannot cancel Purchase Orders because they have %(count)d "
                    "posted vendor bill(s). Please manage the POs manually first.",
                    count=len(posted_bills),
                )
            )

    def _cancel_draft_subcontract_vendor_bills(self):
        draft_bills = self._get_draft_subcontract_vendor_bills()
        if draft_bills:
            draft_bills.button_cancel()
            for purchase_order in self._get_active_subcontract_purchase_orders():
                cancelled_bills = purchase_order.invoice_ids & draft_bills
                if not cancelled_bills:
                    continue
                purchase_order.message_post(
                    body=self.env._(
                        "%(count)d draft vendor bill(s) cancelled before "
                        "cancelling the subcontract Purchase Order.",
                        count=len(cancelled_bills),
                    )
                )
        return draft_bills

    def _cancel_active_subcontract_purchase_orders(self):
        purchase_orders = self._get_active_subcontract_purchase_orders()
        if purchase_orders:
            self._check_subcontract_purchase_orders_can_be_cancelled()
            self._cancel_draft_subcontract_vendor_bills()
            purchase_orders.button_cancel()
        return purchase_orders

    def _create_subcontract_po(self):
        """Create a draft Purchase Order for the subcontractor.

        Called by the server action linked to the 'Assigned' stage
        (or equivalent). Only creates a PO if:
        - The assigned worker or its parent is a subcontractor
        - The FSO template has a subcontracting product configured.
        - No PO is already linked to this FSO

        Errors are logged to the chatter instead of raising exceptions,
        to avoid blocking the stage transition.
        """
        message_no_subcontracting = self.env._(
            "The subcontracting purchase order cannot be created:"
        )
        for order in self:
            if order._get_active_subcontract_purchase_orders():
                continue
            subcontracting_errors = []
            partner_id = order._get_subcontract_vendor()
            if not order.person_id:
                subcontracting_errors.append(
                    self.env._("It does not have an assigned worker.")
                )
            elif not partner_id:
                order.message_post(
                    body=self.env._(
                        "No subcontract Purchase Order was created because "
                        "the assigned worker '%(worker)s' is an internal worker.",
                        worker=order.person_id.name,
                    )
                )
                continue
            if not order.template_id.subcontract_product_id:
                subcontracting_errors.append(
                    self.env._(
                        "The outsourcing product is not configured in "
                        "the template '%(template_name)s'.",
                        template_name=order.template_id.name
                        if order.template_id
                        else self.env._("(none)"),
                    )
                )
            else:
                subcontracting_errors.extend(
                    order._get_subcontract_product_configuration_errors()
                )

            if partner_id and partner_id.supplier_rank < 1:
                subcontracting_errors.append(
                    self.env._(
                        "Subcontractor '%(partner)s' is not associated as a supplier.",
                        partner=partner_id.name,
                    )
                )

            if subcontracting_errors:
                body = Markup("%s<ul><li>%s</li></ul>") % (
                    message_no_subcontracting,
                    Markup("</li><li>").join(subcontracting_errors),
                )
                order.message_post(body=body)
                continue

            purchase_order_vals = order._prepare_subcontract_po_vals()
            purchase_order_id = self.env["purchase.order"].create(purchase_order_vals)
            order.message_post(
                body=self.env._(
                    "Subcontract Purchase Order: "
                    " %(link_purchase_order)s "
                    "created for vendor %(vendor)s.",
                    link_purchase_order=purchase_order_id._get_html_link(),
                    vendor=partner_id.name,
                ),
            )

    def _get_subcontract_vendor(self):
        self.ensure_one()
        partner = self.person_id.partner_id
        if partner.parent_id and partner.parent_id.is_fsm_subcontractor:
            return partner.parent_id
        if partner.is_fsm_subcontractor:
            return partner
        return False

    def _get_subcontract_product_configuration_errors(self):
        self.ensure_one()
        product = self.template_id.subcontract_product_id
        partner = self._get_subcontract_vendor()
        errors = []

        if product.type != "service":
            errors.append(
                self.env._(
                    "The outsourcing product '%(product)s' must be a service.",
                    product=product.display_name,
                )
            )
        if product.purchase_method != "receive":
            errors.append(
                self.env._(
                    "The outsourcing product '%(product)s' must bill based on "
                    "received quantities.",
                    product=product.display_name,
                )
            )
        if partner and not product._select_seller(
            partner_id=partner,
            quantity=self.scheduled_duration or 1.0,
            date=fields.Date.context_today(self),
            uom_id=product.uom_id,
        ):
            errors.append(
                self.env._(
                    "The outsourcing product '%(product)s' has no vendor price "
                    "configured for '%(vendor)s'.",
                    product=product.display_name,
                    vendor=partner.display_name,
                )
            )
        return errors

    def _prepare_subcontract_po_vals(self):
        """
        Prepare the values dict for the subcontract Purchase Order.
        :return: Dict of values
        """
        self.ensure_one()
        product = self.template_id.subcontract_product_id
        partner_id = self._get_subcontract_vendor()
        analytic_distribution = {}
        if self.project_id and self.project_id.account_id:
            analytic_distribution[str(self.project_id.account_id.id)] = 100.0

        purchase_line_vals = {
            "product_id": product.id,
            "name": self.env._("Subcontracted service: %(fso)s", fso=self.name),
            "product_qty": self.scheduled_duration,
            "product_uom": product.uom_id.id,
            "date_planned": self.scheduled_date_end,
        }
        if analytic_distribution:
            purchase_line_vals["analytic_distribution"] = analytic_distribution

        return {
            "partner_id": partner_id.id if partner_id else False,
            "fsm_order_id": self.id,
            "date_planned": self.scheduled_date_end,
            "project_id": self.project_id.id,
            "origin": self.name,
            "order_line": [(0, 0, purchase_line_vals)],
        }

    def _update_subcontract_po_date_planned(self):
        for order in self:
            purchase_orders = order._get_active_subcontract_purchase_orders()
            if purchase_orders:
                purchase_orders.write(
                    {
                        "date_planned": order.scheduled_date_end,
                    }
                )
                purchase_orders.order_line.filtered(
                    lambda line: not line.display_type
                ).write(
                    {
                        "date_planned": order.scheduled_date_end,
                    }
                )

    def _update_subcontract_po_qty(self):
        """Update PO line quantity with actual FSO timesheet hours.

        Called by the server action linked to the 'Done' stage.
        The source of hours is agnostic; they may be logged by
        internal staff or by the vendor.
        """
        for order in self:
            purchase_order_ids = order._get_active_subcontract_purchase_orders()
            if not purchase_order_ids:
                continue
            total_hours = sum(order.mapped("timesheet_ids.unit_amount"))
            if not order.template_id.subcontract_product_id:
                continue
            for purchase_order in purchase_order_ids:
                po_line = purchase_order.order_line.filtered(
                    lambda line, product=order.template_id.subcontract_product_id: (
                        line.product_id == product
                    )
                )[:1]
                if po_line:
                    po_line.write(
                        {
                            "qty_received": total_hours,
                        }
                    )
                    purchase_order.message_post(
                        body=self.env._(
                            "Delivered quantity updated to %(hours).2f hours "
                            "from FSO %(fso)s.",
                            hours=total_hours,
                            fso=order.name,
                        ),
                    )
