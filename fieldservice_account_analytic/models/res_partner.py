# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        access_rights_uid=None,
    ):
        args = args or []
        context = dict(self._context) or {}
        if (
            context.get("location_id")
            and self.env.user.company_id.fsm_filter_location_by_contact
        ):
            location = self.env["fsm.location"].browse(context.get("location_id"))
            args.extend(
                [
                    ("service_location_id", "=", location.id),
                ]
            )
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
        )
