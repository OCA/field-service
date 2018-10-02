# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Urgent'),
]



STATES = [
    ('new', 'New'),
    ('confirmed', 'Confirmed'),
    ('scheduled', 'Scheduled'),
    ('assigned', 'Assigned'),
    ('en_route', 'En Route'),
    ('started', 'Started'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled')]



class FSMStage(models.Model):
    _name = 'fsm.stage'
    _description = 'Field Service Stage'
    _order = 'sequence, name, id'

    name = fields.Char(
        string='Stage Name', 
        required=True, 
        translation=True)
    sequence = fields.Integer(
        'Sequence', 
        default=1,
        help="Used to order stages. Lower is better.")
    description = fields.Text(translation=True)
    is_default = fields.Boolean(
        'Is Default?',
        help='Used by default in new Teams')
    state = fields.Selection(
        STATES, 
        required=True,
        default=STATES[0][0])
    team_ids = fields.Many2many(
        'fsm.team',
        string='Used in Teams')
    legend_priority = fields.Text(
        'Priority Management Explanation',
        translate=True,
        help='Explanation text to help users using'
            ' the star and priority mechanism on'
            ' stages or orders that are in this'
            ' stage.')
    fold = fields.Boolean(
        'Folded in Kanban',
        help='This stage is folded in the kanban view when '
             'there are no record in that stage to display.')
