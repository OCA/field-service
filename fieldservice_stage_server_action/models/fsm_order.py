# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FSMOrder(models.Model):
    _name = "fsm.order"
    _inherit = ["fsm.order", "fsm.stage.server.action.mixin"]
