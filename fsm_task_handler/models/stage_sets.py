from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval


# model for stage sets
class StageSets(models.Model):
    _name = 'fsm.stage.sets'

    name = fields.Char(
            string="Stage Set Name"
    )
    # we will select the stages we need to use and set the attributes
    # like, condition, role, etc
    stage_ids = fields.One2many('selected.stages',
                                'stage_set',
                                string="Stages"
                                )


class SelectedStages(models.Model):
    _name = 'selected.stages'
    _order = 'sequence ASC'

    sequence = fields.Integer()
    stage_set = fields.Many2one('fsm.stage.sets',
                                string="Stage Set"
                                )
    stage_id = fields.Many2one('fsm.stages',
                               string="State",
                               required=True
                               )
    # conditions to change state
    conditions = fields.Text(string="Conditions")
    # roles, who can change state
    role_everyone = fields.Boolean(string="Everyone",
                                   help="Allows anyone to change the state"
                                   )
    role_admin = fields.Boolean(string="Admin",
                                default=True,
                                help="Admin can change stage"
                                )
    role_manager = fields.Boolean(string="Manager",
                                  help="FSM Manager can change stage"
                                  )
    role_team_lead = fields.Boolean(string="Team Leader",
                                    help="Assigne team lead can change stage"
                                    )
    role_emp = fields.Boolean(string="Person",
                              help="Members of assigned "
                                   "teams can change stage"
                              )

    # we need to specify the stage where the work starts,
    #  to automatically start the related workitem
    start_stage = fields.Boolean(string="Staring stage")
    finish_stage = fields.Boolean(string="Final stage")

    # need to include transitions
    use_trasitions = fields.Boolean(string="Use advanced transitions",
                                    default=False
                                    )
    transition_ids = fields.One2many('stage.transition.line',
                                     'selected_stage_id',
                                     string="Transition lines"
                                     )

    def check_domain(self):
        """We are evaluating the expression provided
        is syntactically correct or not"""
        eval_result = None
        try:
            safe_eval(self.conditions)
        except Exception as e:
            eval_result = e
        if eval_result:
            raise eval_result
        else:
            raise exceptions.Warning(_('This expression seems fine!'))
