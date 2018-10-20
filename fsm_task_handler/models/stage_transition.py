from odoo import fields, models


class StageTransitionAuthority(models.Model):
    _name = 'stage.transition.authority'

    name = fields.Char(string="Name",
                       required=True
                       )


class StageTransitionLines(models.Model):
    _name = 'stage.transition.line'
    _description = 'Manages advanced stage transitions'
    _rec_name = 'dest_stage'

    selected_stage_id = fields.Many2one('selected.stages')
    # destination stage
    dest_stage = fields.Many2one('fsm.stages',
                                 string="Destination"
                                 )
    # condition to be validated before performing the transition
    validate_transition = fields.Text(string="Conditions")
    # transition allowed authorities
    transition_allowed = fields.Many2many('stage.transition.authority',
                                          string="Stage Transition authority")
