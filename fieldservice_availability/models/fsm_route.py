# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRouteDeliveryScheduleLine(models.Model):
    _name = "fsm.route.delivery.schedule.line"
    _inherit = "fsm.delivery.schedule.line.mixin"
    _description = "FSM Route Delivery Schedule Line"

    route_id = fields.Many2one(
        "fsm.route", string="Route", required=True, ondelete="cascade"
    )


class FSMRoute(models.Model):
    _name = "fsm.route"
    _inherit = ["fsm.route", "fsm.delivery.schedule.mixin"]

    default_schedule_line_ids = fields.One2many(
        "fsm.route.delivery.schedule.line",
        "route_id",
        domain=[("is_seasonal", "=", False)],
        string="Default Day Schedules",
    )

    seasonal_schedule_line_ids = fields.One2many(
        "fsm.route.delivery.schedule.line",
        "route_id",
        domain=[("is_seasonal", "=", True)],
        string="Seasonal Day Schedules",
    )

    def get_allowed_route_days(self):
        """Returns allowed fsm.route.day recordset for this route,
        company default, or all active days."""
        self.ensure_one()
        return (
            self.day_ids
            or self.env.company.fsm_default_route_day_ids
            or self.env["fsm.route.day"].search([])
        )
