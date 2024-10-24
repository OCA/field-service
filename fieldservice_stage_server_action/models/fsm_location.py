# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FSMLocation(models.Model):
    _name = "fsm.location"
    _inherit = ["fsm.location", "fsm.stage.server.action.mixin"]
