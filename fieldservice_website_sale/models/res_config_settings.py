# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    max_date_number = fields.Selection(
        selection=[(str(i), str(i)) for i in range(1, 13)],
        default="1",
        required=True,
    )

    max_date_unit = fields.Selection(
        selection=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
        default="months",
        required=True,
    )

    time_range_default_id = fields.Many2one(
        "fsm.delivery.time.range",
        string="Default Delivery Time Range",
        help="Time range to auto-assign when 'Auto-assign "
        "default delivery time range' is enabled.",
    )

    auto_assign_default_time_range = fields.Boolean(
        string="Auto-assign default delivery time range",
        default=False,
        help="If enabled, a default delivery time range will be "
        "auto-assigned when not selected by the user.",
    )

    @api.model
    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].set_param(
            "fieldservice.max_date_number", self.max_date_number
        )
        self.env["ir.config_parameter"].set_param(
            "fieldservice.max_date_unit", self.max_date_unit
        )
        self.env["ir.config_parameter"].set_param(
            "fieldservice.auto_assign_default_time_range",
            self.auto_assign_default_time_range,
        )
        self.env["ir.config_parameter"].set_param(
            "fieldservice.time_range_default_id",
            self.time_range_default_id.id if self.time_range_default_id.id else False,
        )
        return True

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        time_range_default_id = params.get_param(
            "fieldservice.time_range_default_id", False
        )
        res.update(
            max_date_number=params.get_param("fieldservice.max_date_number", "1"),
            max_date_unit=params.get_param("fieldservice.max_date_unit", "months"),
            auto_assign_default_time_range=params.get_param(
                "fieldservice.auto_assign_default_time_range", "False"
            )
            == "True",
            time_range_default_id=(
                int(time_range_default_id)
                if time_range_default_id and time_range_default_id.isdigit()
                else False
            ),
        )
        return res
