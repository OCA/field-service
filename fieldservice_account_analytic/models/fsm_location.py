# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", company_dependent=True
    )

    @api.model
    def get_default_customer(self):
        if self.fsm_parent_id:
            return self.fsm_parent_id.customer_id.id
        return self.owner_id.id

    customer_id = fields.Many2one(
        "res.partner",
        string="Billed Customer",
        required=True,
        ondelete="restrict",
        auto_join=True,
        tracking=True,
        default=get_default_customer,
    )

    @api.onchange("fsm_parent_id")
    def _onchange_fsm_parent_id_account(self):
        self.customer_id = self.fsm_parent_id.customer_id or False

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        access_rights_uid=None,
    ):
        args = args or []
        context = dict(self._context) or {}
        if context.get("customer_id"):
            partner = self.env["res.partner"].browse(context.get("customer_id"))
            args.extend(
                [
                    ("partner_id", "=", partner.id),
                ]
            )
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
        )
