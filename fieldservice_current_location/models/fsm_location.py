# Copyright 2026 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmLocation(models.Model):
    _inherit = "fsm.location"

    place = fields.Char()
