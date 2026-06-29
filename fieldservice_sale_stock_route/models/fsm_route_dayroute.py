# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMRouteDayRoute(models.Model):
    _inherit = "fsm.route.dayroute"

    @api.constrains("date", "route_id")
    def check_day(self):
        for rec in self:
            if rec.route_id and rec.route_id.force_schedule:
                return

        super().check_day()
