# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMDeliveryTimeRange(models.Model):
    _name = "fsm.delivery.time.range"
    _description = "Delivery Time Range"
    _order = "sequence, start_time asc"

    name = fields.Char(compute="_compute_name", store=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    route_id = fields.Many2one(
        "fsm.route",
        string="Route",
        help="Specific route this time range applies to. "
        "Leave empty for global time ranges.",
    )
    sequence = fields.Integer(
        default=10,
        help="Customize the order of time ranges. Lower numbers are shown first.",
    )

    @api.depends("start_time", "end_time")
    def _compute_name(self):
        for record in self:
            start = "{:02d}:{:02d}".format(*divmod(int(record.start_time * 60), 60))
            end = "{:02d}:{:02d}".format(*divmod(int(record.end_time * 60), 60))
            record.name = f"{start} - {end}"

    @api.constrains("start_time", "end_time")
    def _check_time_range(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError(
                    _("The start time must be earlier than the end time.")
                )
