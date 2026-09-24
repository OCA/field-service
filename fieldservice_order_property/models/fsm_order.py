# Copyright 2026 Binhex - Rolando Pérez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    fsm_order_properties = fields.Properties(
        "Properties",
        definition="team_id.fsm_order_properties_definition",
        copy=True,
    )
