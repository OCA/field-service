# Copyright (C) 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    is_invoiceable = fields.Boolean(copy=False)
