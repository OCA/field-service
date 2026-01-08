# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    location_size_ids = fields.One2many(
        "fsm.location.size", "location_id", string="Location Sizes"
    )
