# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    vendor_bill_ids = fields.Many2many(
        "account.move",
        string="Vendor bills",
        tracking=True,
        copy=False,
        domain=[("move_type", "in", ["in_invoice", "in_refund"])],
    )
