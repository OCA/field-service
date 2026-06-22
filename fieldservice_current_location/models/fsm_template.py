# Copyright 2026 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTemplate(models.Model):
    _inherit = "fsm.template"

    use_current_location = fields.Boolean(
        help="Allow using current location for orders based on this template",
    )

    show_use_current_location = fields.Boolean(
        compute="_compute_show_use_current_location",
        store=False,
    )

    def _compute_show_use_current_location(self):
        config_restrict = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fieldservice.restrict_current_location_in_templates", False)
        )
        for record in self:
            record.show_use_current_location = config_restrict
