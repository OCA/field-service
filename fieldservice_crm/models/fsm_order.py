# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    opportunity_id = fields.Many2one("crm.lead", tracking=True)
    opportunity_customer_vat = fields.Char(
        related="opportunity_id.partner_id.vat", string="Customer VAT"
    )
    sales_person_id = fields.Many2one(
        "res.users",
        compute="_compute_sales_person_id",
        string="Salesperson",
        readonly=False,
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        if self._has_dispacher_group():
            for vals in vals_list:
                if not vals.get("opportunity_id") and not vals.get("sales_person_id"):
                    vals["sales_person_id"] = self.env.user.id
        return super().create(vals_list)

    @api.depends("opportunity_id", "opportunity_id.user_id")
    def _compute_sales_person_id(self):
        has_dispacher_group = self._has_dispacher_group()
        for order in self:
            if order.opportunity_id and order.opportunity_id.user_id:
                order.sales_person_id = order.opportunity_id.user_id
            elif not order.sales_person_id:
                if has_dispacher_group:
                    order.sales_person_id = self.env.user
                else:
                    order.sales_person_id = False

    def _has_dispacher_group(self):
        return self.env.user.has_group("fieldservice.group_fsm_dispatcher")
