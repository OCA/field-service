# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    fsm_route_id = fields.Many2one(comodel_name="fsm.route", string="Route")

    def write(self, vals):
        res = super().write(vals)
        if "fsm_route_id" in vals:
            orders = self.env["fsm.order"].search(
                [
                    ("location_id", "in", self.ids),
                    ("scheduled_date_start", "!=", False),
                ]
            )
            for order in orders:
                order._reassign_dayroute_for_person_timezone()
        return res
