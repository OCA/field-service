# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FieldServiceBlackoutGroup(models.Model):
    _name = "fsm.blackout.group"
    _description = "Blackout Group"

    name = fields.Char(required=True)
    fsm_blackout_day_ids = fields.Many2many(
        "fsm.blackout.day",
        "fsm_blackout_group_ids",
        "fsm_blackout_group_id",
        "fsm_blackout_day_id",
        string="Days",
    )
