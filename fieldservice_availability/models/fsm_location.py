# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    delivery_time_range_ids = fields.Many2many(
        comodel_name="fsm.delivery.time.range",
        relation="fsm_location_delivery_time_range_rel",
        column1="location_id",
        column2="time_range_id",
        string="Delivery Time Ranges",
        help="Specific schedules for this location (overrides route defaults).",
    )

    @api.constrains("delivery_time_range_ids")
    def _check_unique_default_schedule(self):
        for location in self:
            default_schedules = location.delivery_time_range_ids.filtered(
                lambda r: not r.is_seasonal
            )
            if len(default_schedules) > 1:
                raise ValidationError(
                    _(
                        "Location '%s' cannot have more than 1 default schedule "
                        "(without dates)."
                    )
                    % location.name
                )

    def _resolve_active_ranges(self, records, target_date):
        """Helper method to filter active seasonal or default
        ranges from a recordset."""
        seasonal = records.filtered(
            lambda r: r.is_seasonal and r.is_active_on_date(target_date)
        )
        if seasonal:
            return seasonal
        return records.filtered(lambda r: not r.is_seasonal)

    def get_delivery_time_ranges(self, target_date=None):
        """Resolves active delivery time ranges following hierarchy:
        1. Location seasonal schedule active on target_date
        2. Location default schedule
        3. Route seasonal schedule active on target_date
        4. Route default schedule
        5. Global fallback schedule
        """
        self.ensure_one()
        if not target_date:
            target_date = fields.Date.context_today(self)
        elif isinstance(target_date, datetime):
            target_date = target_date.date()

        # 1 & 2. Location scope
        if self.delivery_time_range_ids:
            ranges = self._resolve_active_ranges(
                self.delivery_time_range_ids, target_date
            )
            if ranges:
                return ranges

        # 3 & 4. Route scope
        if self.fsm_route_id and self.fsm_route_id.delivery_time_range_ids:
            ranges = self._resolve_active_ranges(
                self.fsm_route_id.delivery_time_range_ids, target_date
            )
            if ranges:
                return ranges

        # 5. Global Fallback scope
        return self.env["fsm.delivery.time.range"].search(
            [("is_seasonal", "=", False)], limit=1
        )
