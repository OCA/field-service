# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMRoute(models.Model):
    _name = "fsm.route"
    _description = "Field Service Route"

    name = fields.Char(required=True)
    fsm_person_id = fields.Many2one(comodel_name="fsm.person", string="Person")
    day_ids = fields.Many2many(comodel_name="fsm.route.day", string="Days")
    max_order = fields.Integer(
        string="Maximum Orders",
        default=0,
        help="Maximum number of orders per day route.",
    )

    def run_on(self, date):
        """
        :param date: date
        :return: True if the route runs on the date, False otherwise.
        """
        if date:
            day_index = date.weekday()
            day = self.env.ref("fieldservice_route.fsm_route_day_" + str(day_index))
            return day in self.day_ids

    def write(self, vals):
        res = super().write(vals)
        if "fsm_person_id" in vals:
            orders = self.env["fsm.order"].search(
                [
                    ("fsm_route_id", "in", self.ids),
                    ("scheduled_date_start", "!=", False),
                ]
            )
            for order in orders:
                order._reassign_dayroute_for_person_timezone()
        return res
