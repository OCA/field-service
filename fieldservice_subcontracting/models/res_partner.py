# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_fsm_subcontractor = fields.Boolean(string="Is Subcontractor?")

    @api.constrains("is_fsm_subcontractor")
    def _check_subcontractor_is_vendor(self):
        for partner in self:
            if partner.is_fsm_subcontractor and partner.supplier_rank < 1:
                raise ValidationError(
                    self.env._(
                        "Worker '%(worker)s' is marked as subcontractor but "
                        "their partner '%(partner)s' is not configured as a "
                        "vendor. Please set the partner as a vendor first.",
                        worker=partner.name,
                        partner=partner.name,
                    )
                )
