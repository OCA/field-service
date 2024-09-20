# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    serviceprofile_ids = fields.Many2many(
        "agreement.serviceprofile",
        string="Service Profiles",
        compute="_compute_serviceprofile_ids",
    )

    def _compute_serviceprofile_ids(self):
        if not self.ids:
            self.serviceprofile_ids = False
            return
        agreements_by_location = dict(
            self.env["agreement"]._read_group(
                [("fsm_location_id", "in", self.ids)],
                ["fsm_location_id"],
                ["id:recordset"],
            )
        )
        serviceprofiles_by_agreement = dict(
            self.env["agreement.serviceprofile"]._read_group(
                [("agreement_id.fsm_location_id", "in", self.ids)],
                ["agreement_id"],
                ["id:recordset"],
            )
        )
        serviceprofiles_by_location = {
            location: self.env["agreement.serviceprofile"].browse(
                set(
                    itertools.chain.from_iterable(
                        serviceprofiles_by_agreement[agreement].ids
                        for agreement in agreements
                        if agreement in serviceprofiles_by_agreement
                    )
                )
            )
            for location, agreements in agreements_by_location.items()
        }
        for rec in self:
            rec.serviceprofile_ids = serviceprofiles_by_location.get(rec)
