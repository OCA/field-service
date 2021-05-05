# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    serviceprofile_ids = fields.Many2many(
        "agreement.serviceprofile",
        string="Service Profiles",
        compute="_compute_service_ids",
    )

    def _compute_service_ids(self):
        for loc in self:
            agreements = self.env["agreement"].search(
                [("fsm_location_id", "=", loc.id)]
            )
            ids = []
            for agree in agreements:
                servpros = self.env["agreement.serviceprofile"].search(
                    [("agreement_id", "=", agree.id)]
                )
                for ser in servpros:
                    if ser.id not in ids:
                        ids.append(ser.id)
            loc.serviceprofile_ids = ids
