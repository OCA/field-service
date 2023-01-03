# Copyright (C) 2022 - TODAY, Rafnix Guzmán
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    def _compute_access_url(self):
        for record in self:
            record.access_url = f"/my/locations/{record.id}"
