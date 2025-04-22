# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRoute(models.Model):
    _inherit = "fsm.route"

    fsm_blackout_group_ids = fields.Many2many(
        "fsm.blackout.group",
        "fsm_route_ids",
        "fsm_route_id",
        "fsm_blackout_group_id",
        string="Blackout Group Days",
    )
