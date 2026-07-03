# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrderCancelConfirm(models.TransientModel):
    _name = "fsm.order.cancel.confirm"
    _description = "Confirm FSO Cancellation with PO Cancellation"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Field Service Order",
        required=True,
        readonly=True,
    )
    purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Purchase Orders",
        compute="_compute_purchase_order_ids",
        readonly=True,
    )
    warning_message = fields.Text(
        compute="_compute_warning_message",
    )

    @api.depends("fsm_order_id.purchase_order_ids.state")
    def _compute_purchase_order_ids(self):
        for wizard in self:
            wizard.purchase_order_ids = (
                wizard.fsm_order_id._get_active_subcontract_purchase_orders()
            )

    @api.depends(
        "fsm_order_id.purchase_order_ids.invoice_ids.state",
        "fsm_order_id.purchase_order_ids.state",
    )
    def _compute_warning_message(self):
        for wizard in self:
            posted_bills = wizard.fsm_order_id._get_posted_subcontract_vendor_bills()
            if posted_bills:
                wizard.warning_message = self.env._(
                    "One or more related Purchase Orders have posted vendor "
                    "bills and cannot be cancelled automatically."
                )
            elif wizard.purchase_order_ids:
                wizard.warning_message = self.env._(
                    "This Field Service Order has active Purchase Orders "
                    "%(purchase_orders)s. Do you want to cancel them too?",
                    purchase_orders=", ".join(wizard.purchase_order_ids.mapped("name")),
                )
            else:
                wizard.warning_message = ""

    def _cancel_fsm_order(self):
        self.ensure_one()
        self.fsm_order_id.with_context(
            skip_subcontract_cancel_wizard=True
        ).action_cancel()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_cancel_fsm_only(self):
        """Cancel the FSO and keep related Purchase Orders open."""
        return self._cancel_fsm_order()

    def action_cancel_fsm_and_purchase_orders(self):
        """Cancel related Purchase Orders and then cancel the FSO."""
        self.ensure_one()
        self.fsm_order_id._cancel_active_subcontract_purchase_orders()
        return self._cancel_fsm_order()
