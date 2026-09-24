# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMRoute(models.Model):
    _inherit = "fsm.route"

    delivery_time_range_ids = fields.Many2many(
        comodel_name="fsm.delivery.time.range",
        relation="fsm_route_delivery_time_range_rel",
        column1="route_id",
        column2="time_range_id",
        string="Default Delivery Time Ranges",
        help="Default schedules for this route.",
    )

    @api.constrains("delivery_time_range_ids")
    def _check_unique_default_schedule(self):
        for route in self:
            default_schedules = route.delivery_time_range_ids.filtered(
                lambda r: not r.is_seasonal
            )
            if len(default_schedules) > 1:
                raise ValidationError(
                    _(
                        "Route '%s' cannot have more than 1 default schedule "
                        "(without dates)."
                    )
                    % route.name
                )
