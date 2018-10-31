# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _inherit = 'maintenance.stage'
    _description = 'Field Service Stage'
    _order = 'sequence, name, id'

    legend_priority = fields.Text('Priority Management Explanation',
                                  translate=True,
                                  help='Explanation text to help users using'
                                       ' the star and priority mechanism on'
                                       ' stages or orders that are in this'
                                       ' stage.')
