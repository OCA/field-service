# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    sales_territory_id = fields.Many2one('fsm.territory',
                                         string='Sales Territory')
