# Copyright (C) 2022 Raphaël Reverdy (Akretion)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import Domain


class FSMTeam(models.Model):
    _inherit = "fsm.team"

    def _compute_recurring_draft_count(self):
        order_data = self.env["fsm.recurring"]._read_group(
            domain=Domain.AND(
                [
                    Domain("team_id", "in", self.ids),
                    Domain("state", "=", "draft"),
                ]
            ),
            groupby=["team_id"],
            aggregates=["__count"],
        )
        for team in self:
            count_data = next(filter(lambda r: r[0] == team, order_data), None)
            team.recurring_draft_count = count_data[1] if count_data else 0

    recurring_draft_count = fields.Integer(
        compute="_compute_recurring_draft_count", string="Recurring in draft"
    )
