# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_id = fields.Many2one("sale.order")
    sale_line_id = fields.Many2one("sale.order.line")

    def action_create_quotation(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_new")
        partner = self.location_id.owner_id or self.location_id.partner_id
        action["context"] = {
            "default_partner_id": partner.id,
            "default_fsm_location_id": self.location_id.id,
            "default_origin": self.name,
            "default_company_id": self.company_id.id,
        }
        # If opportunity_id is present (from fieldservice_crm)
        if hasattr(self, "opportunity_id") and self.opportunity_id:
            action["context"]["default_opportunity_id"] = self.opportunity_id.id
        return action

    def action_view_sales(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_line_id.order_id.id or self.sale_id.id,
            "context": {"create": False},
            "name": _("Sales Orders"),
        }
