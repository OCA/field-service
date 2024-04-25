# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models

from .validate_utils import validate_stage_fields


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.constrains("stage_id")
    def _validate_stage_fields(self):
        validate_stage_fields(self)
