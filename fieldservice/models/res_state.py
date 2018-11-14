# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    territory_id = fields.Many2one('fsm.territory', string="Territory")
