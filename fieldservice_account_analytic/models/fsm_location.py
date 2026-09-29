# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", company_dependent=True
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Billed Customer",
        compute="_compute_customer_id",
        store=True,
        readonly=False,
        precompute=True,
        required=True,
        ondelete="restrict",
        auto_join=True,
        tracking=True,
    )

    @api.depends("fsm_parent_id", "owner_id")
    def _compute_customer_id(self):
        """Default the billed customer to the one of the parent location,
        or to the location owner. A customer explicitly set by the user
        is only overridden when the parent location provides one."""
        for location in self:
            location.customer_id = (
                location.fsm_parent_id.customer_id
                or location.customer_id
                or location.owner_id
            )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        domain = domain or []
        if self.env.context.get("customer_id"):
            domain = expression.AND(
                [domain, [("partner_id", "=", self.env.context["customer_id"])]]
            )
        return super()._search(domain, offset=offset, limit=limit, order=order)
