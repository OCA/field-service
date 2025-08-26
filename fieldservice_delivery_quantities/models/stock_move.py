# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    fsm_dayroute_id = fields.Many2one(
        "fsm.route.dayroute",
        related="fsm_order_id.dayroute_id",
        string="Day Route",
        store=True,
    )

    fsm_worker_id = fields.Many2one(
        "fsm.person",
        related="fsm_order_id.person_id",
        string="Worker",
        store=True,
    )

    fsm_location_id = fields.Many2one(
        "fsm.location",
        related="fsm_order_id.location_id",
        string="Location",
        store=True,
    )

    route_name = fields.Char(
        related="fsm_dayroute_id.route_id.name",
        string="Route",
        store=True,
    )
