# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FSMPerson(models.Model):
    _name = "fsm.person"
    _inherit = ["fsm.person", "fsm.stage.server.action.mixin"]
