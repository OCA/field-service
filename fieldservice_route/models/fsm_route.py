# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
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
