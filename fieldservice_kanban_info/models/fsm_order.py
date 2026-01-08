# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    schedule_time_range = fields.Char(compute="_compute_schedule_time_range")

    @api.depends("scheduled_date_start", "scheduled_date_end")
    def _compute_schedule_time_range(self):
        time_range_format = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fieldservice.schedule_time_range_format", "time_only")
        )

        lang = self.env.user.lang
        lang_obj = self.env["res.lang"]._lang_get(lang)
        date_format = lang_obj.date_format
        time_format = lang_obj.time_format.replace(":%S", "").strip()
        lang_format = f"{date_format} {time_format}"

        for order in self:
            if not order.scheduled_date_start:
                order.schedule_time_range = False
                continue

            start = fields.Datetime.context_timestamp(order, order.scheduled_date_start)
            end = fields.Datetime.context_timestamp(order, order.scheduled_date_end)

            # Prevent double space errors (e.g., "02/27/2025 15:30 AM")
            start_str = start.strftime(lang_format)
            start_date, start_time = start_str.split(" ", 1)
            end_str = end.strftime(lang_format)
            end_date, end_time = end_str.split(" ", 1)

            if time_range_format == "date_and_time":
                range_str = (
                    f"{start_date} {start_time} - {end_time}"
                    if start.date() == end.date()
                    else f"{start_date} {start_time} - {end_date} {end_time}"
                )
            else:
                range_str = f"{start_time} - {end_time}"

            order.schedule_time_range = range_str
