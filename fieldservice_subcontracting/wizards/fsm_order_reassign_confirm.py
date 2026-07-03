# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrderReassignConfirm(models.TransientModel):
    _name = "fsm.order.reassign.confirm"
    _description = "Confirm FSO Worker Reassignment with PO Cancellation"

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
    new_person_id = fields.Many2one(
        comodel_name="fsm.person",
        string="New Worker",
        required=True,
    )
    warning_message = fields.Text(
        compute="_compute_warning_message",
    )

    @api.depends("fsm_order_id.purchase_order_ids.state")
    def _compute_purchase_order_ids(self):
        for wiz in self:
            wiz.purchase_order_ids = (
                wiz.fsm_order_id._get_active_subcontract_purchase_orders()
            )

    @api.depends(
        "fsm_order_id.purchase_order_ids.invoice_ids.state",
        "fsm_order_id.purchase_order_ids.state",
    )
    def _compute_warning_message(self):
        for wiz in self:
            posted_bills = wiz.fsm_order_id._get_posted_subcontract_vendor_bills()
            if posted_bills:
                wiz.warning_message = self.env._(
                    "One or more Purchase Orders have posted vendor bills and "
                    "cannot be cancelled automatically. You must manage the "
                    "POs manually before reassigning the worker."
                )
            elif wiz.purchase_order_ids:
                wiz.warning_message = self.env._(
                    "Reassigning the worker will cancel Purchase Orders "
                    "%(purchase_orders)s. Do you want to proceed?",
                    purchase_orders=", ".join(wiz.purchase_order_ids.mapped("name")),
                )
            else:
                wiz.warning_message = ""

    def action_confirm(self):
        """Cancel the POs and proceed with worker reassignment."""
        self.ensure_one()
        self.fsm_order_id._check_reassign_subcontract_worker_allowed()
        self.fsm_order_id._cancel_active_subcontract_purchase_orders()
        self.fsm_order_id.with_context(skip_reassign_check=True).write(
            {"person_id": self.new_person_id.id}
        )
        self.fsm_order_id._create_subcontract_po()
        return {"type": "ir.actions.act_window_close"}
