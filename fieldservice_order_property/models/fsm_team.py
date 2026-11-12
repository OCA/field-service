# Copyright 2026 Binhex - Rolando Pérez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _inherit = "fsm.team"

    fsm_order_properties_definition = fields.PropertiesDefinition(
        "FSM Order Properties"
    )
