# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FSMEquipment(models.Model):
    _name = "fsm.equipment"
    _inherit = ["fsm.equipment", "fsm.stage.server.action.mixin"]
