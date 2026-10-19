# Copyright 2026 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fsm_default_route_day_ids = fields.Many2many(
        comodel_name="fsm.route.day",
        relation="fsm_company_route_day_rel",
        column1="company_id",
        column2="day_id",
        string="Default FSM Operational Days",
        help="Default operational days used when no days are "
        "specified on the location or route.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_default_route_day_ids = fields.Many2many(
        related="company_id.fsm_default_route_day_ids",
        readonly=False,
        string="Default FSM Operational Days",
    )
