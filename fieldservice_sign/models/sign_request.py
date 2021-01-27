# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.urls import url_join

from odoo import api, fields, models


class SignRequest(models.Model):
    _inherit = "sign.request"

    fsm_order_id = fields.Many2one("fsm.order", "FSM Order")
    url_link = fields.Char(compute="_compute_url_link", string="URL Link",
                           store=True)

    @api.depends("request_item_ids")
    def _compute_url_link(self):
        for signer in self.request_item_ids:
            base_url = self.env["ir.config_parameter"].get_param(
                "web.base.url")
            url_link = url_join(
                base_url,
                "sign/document/%(request_id)s/%(access_token)s"
                % {
                    "request_id": signer.sign_request_id.id,
                    "access_token": signer.access_token,
                },
            )
            self.url_link = url_link
