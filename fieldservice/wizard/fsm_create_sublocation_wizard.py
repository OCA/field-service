# Copyright (C) 2025 - TODAY, APSL - Nagarro (Bernat Obrador)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreateSubLocationWizard(models.TransientModel):
    _name = "fsm.create.sub.location.wizard"
    _inherit = ["format.address.mixin"]
    _description = "Wizard to Create Sub Location"

    name = fields.Char(compute="_compute_name", store=True)
    parent_location_id = fields.Many2one(
        "fsm.location", string="Parent Location", required=True
    )
    related_owner_id = fields.Many2one(
        "res.partner", string="Related Owner", required=True
    )
    phone = fields.Char()
    email = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one("res.country", string="Country", ondelete="restrict")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get("parent_location_id"):
            parent_location = self.env["fsm.location"].browse(res["parent_location_id"])
            res.update(
                {
                    "related_owner_id": parent_location.owner_id.id,
                    "street": parent_location.street,
                    "street2": parent_location.street2,
                    "zip": parent_location.zip,
                    "state_id": parent_location.state_id.id,
                    "country_id": parent_location.country_id.id,
                    "city": parent_location.city,
                    "phone": parent_location.phone,
                    "email": parent_location.email,
                }
            )
        return res

    @api.depends("parent_location_id", "street", "city")
    def _compute_name(self):
        for wizard in self:
            parts = [wizard.parent_location_id.name]
            if wizard.city != wizard.parent_location_id.city:
                parts.append(wizard.city)
            elif wizard.street != wizard.parent_location_id.street:
                parts.append(wizard.street)
            wizard.name = " - ".join(parts)

    def _get_location_vals(self, partner_id):
        # To avoid conflicts with fieldservice_account_analytic
        vals = {
            "name": self.name,
            "partner_id": partner_id.id,
            "fsm_parent_id": self.parent_location_id.id,
            "owner_id": self.related_owner_id.id,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
        }

        if (
            self.env["ir.module.module"]
            .sudo()
            .search(
                [
                    ("name", "=", "fieldservice_account_analytic"),
                    ("state", "=", "installed"),
                ]
            )
        ):
            vals["customer_id"] = (
                self.parent_location_id.customer_id.id or self.related_owner_id.id
            )

        return vals

    def create_sub_location(self):
        partner_id = self.env["res.partner"].create(
            {
                "name": self.name,
                "parent_id": self.parent_location_id.partner_id.id,
                "street": self.street,
                "street2": self.street2,
                "zip": self.zip,
                "city": self.city,
                "state_id": self.state_id.id,
                "country_id": self.country_id.id,
                "phone": self.phone,
                "email": self.email,
            }
        )
        location = self.env["fsm.location"].create(self._get_location_vals(partner_id))

        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.location",
            "res_id": location.id,
            "view_mode": "form",
            "target": "current",
        }
