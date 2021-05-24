# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fsm_route_id = fields.Many2one(
        comodel_name="fsm.route",
        compute="_compute_fsm_route_id",
        inverse="_inverse_fsm_route_id",
        store=True,
        readonly=False,
    )

    @api.depends("service_location_id.fsm_route_id")
    def _compute_fsm_route_id(self):
        """Get the route from the main partner service location"""
        for partner in self:
            partner.fsm_route_id = partner.service_location_id.fsm_route_id

    def _inverse_fsm_route_id(self):
        """We can set the main service location route from the partner or
        create a service location for the partner if it isn't set"""
        for partner in self:
            if not partner.service_location_id and partner.fsm_route_id:
                self.env["fsm.wizard"].action_convert_location(partner)
                location = self.env["fsm.location"].search(
                    [
                        ("partner_id", "=", partner.id),
                    ],
                    limit=1,
                )
                location.fsm_route_id = partner.fsm_route_id
                partner.service_location_id = location
            if partner.service_location_id:
                partner.service_location_id.fsm_route_id = partner.fsm_route_id
