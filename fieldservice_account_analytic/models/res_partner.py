# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        domain = domain or []
        if (
            self.env.context.get("location_id")
            and self.env.company.fsm_filter_location_by_contact
        ):
            domain = expression.AND(
                [
                    domain,
                    [("service_location_id", "=", self.env.context["location_id"])],
                ]
            )
        return super()._search(domain, offset=offset, limit=limit, order=order)
