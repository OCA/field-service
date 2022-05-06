# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    pricelist_count = fields.Integer(
        compute="_compute_pricelist_count", string="# Pricelists"
    )

    def _compute_pricelist_count(self):
        for worker in self:
            worker.pricelist_count = self.env["product.supplierinfo"].search_count(
                [("name", "=", worker.partner_id.id)]
            )

    def action_view_pricelists(self):
        for worker in self:
            pricelist = self.env["product.supplierinfo"].search(
                [("name", "=", worker.partner_id.id)]
            )
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "product.product_supplierinfo_type_action"
            )
            if len(pricelist) == 1:
                action["views"] = [
                    (self.env.ref("product.product_supplierinfo_form_view").id, "form")
                ]
                action["res_id"] = pricelist.ids[0]
            else:
                action["domain"] = [("id", "in", pricelist.ids)]
            return action
