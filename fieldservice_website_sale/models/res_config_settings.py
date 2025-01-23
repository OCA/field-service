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

    @api.model
    def set_values(self):
        super().set_values()

        self.env["ir.config_parameter"].set_param(
            "fieldservice.max_date_number", self.max_date_number
        )
        self.env["ir.config_parameter"].set_param(
            "fieldservice.max_date_unit", self.max_date_unit
        )
        return True

    @api.model
    def get_values(self):
        res = super().get_values()

        params = self.env["ir.config_parameter"].sudo()
        res.update(
            max_date_number=params.get_param("fieldservice.max_date_number", "1"),
            max_date_unit=params.get_param("fieldservice.max_date_unit", "months"),
        )
        return res
