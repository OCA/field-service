# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Urgent'),
]


class FSMStage(models.Model):
    _name = 'fsm.stage'
    _description = 'Field Service Stage'
    _order = 'sequence, name, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order stages. Lower is better.")
    legend_priority = fields.Text('Priority Management Explanation',
                                  translate=True,
                                  help='Explanation text to help users using'
                                       ' the star and priority mechanism on'
                                       ' stages or orders that are in this'
                                       ' stage.')
    fold = fields.Boolean('Folded in Kanban',
                          help='This stage is folded in the kanban view when '
                               'there are no record in that stage to display.')
    is_closed = fields.Boolean('Is a close stage',
                               help='Services in this stage are considered '
                                    'as closed.')
