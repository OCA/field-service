# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    type = fields.Selection(selection_add=[('repair', 'Repair')])
    repair_id = fields.Many2one(
        'repair.order', 'Repair Order')
