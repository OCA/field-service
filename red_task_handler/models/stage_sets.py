# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval


# model for stages
class StagesFSM(models.Model):
    _name = 'fsm.stages'

    sequence = fields.Integer()
    name = fields.Char(
            string="Stage Name",
            required=True
    )
    fold = fields.Boolean(
            default=True,
            string="Folded in Kanban"
    )
    ref_name = fields.Char(
            string="Reference",
            help="We can use this value to refer this stage."
    )
    ref_editable = fields.Boolean(
            default=True
    )

    @api.model
    def create(self, vals):
        res = super(StagesFSM, self).create(vals)
        # we are creating a constant value which can be used to access this stage
        # this value will be editable only at the time of creation.
        # we are setting a flag(field) to make the reference field readonly

        # if something is provided in the reference section, we will
        # convert it to lowercase and append this stage's id to it
        if vals.get('ref_name'):
            ref_name = vals.get('ref_name').lower()
            ref_name = ref_name.replace(' ', '_')
        else:
            ref_name = res.name.lower()
            ref_name = ref_name.replace(' ', '_')
        res.ref_name = ref_name + '_' + str(res.id)
        # disabling the flag to make the field readonly
        res.ref_editable = False
        return res

    @api.multi
    def write(self, vals):
        res = super(StagesFSM, self).write(vals)
        # just to make sure that the flag is disabled(to make the reference readonly)
        if self.ref_editable:
            self.ref_editable = False
        return res


# model for stage sets
class StageSets(models.Model):
    _name = 'fsm.stage.sets'

    name = fields.Char(
            string="Stage Set Name"
    )
    # we will select the stages we need to use and set the attributes
    # like, condition, role, etc
    stage_ids = fields.One2many(
            'selected.stages',
            'stage_set',
            string="Stages"
    )

    # @api.model
    # def create(self, vals):
    #     start_stage_flag = False
    #     multiple_start = False
    #     finish_stage_flag = False
    #     multiple_ending = False
    #     if vals.get('stage_ids'):
    #         for i in vals.get('stage_ids'):
    #             try:
    #                 if i[2].get('start_stage') and not start_stage_flag:
    #                     start_stage_flag = True
    #                 elif i[2].get('start_stage') and start_stage_flag:
    #                     multiple_start = True
    #                 if i[2].get('finish_stage') and not finish_stage_flag:
    #                     finish_stage_flag = True
    #                 elif i[2].get('finish_stage') and finish_stage_flag:
    #                     multiple_ending = True
    #             except Exception as e:
    #                 pass
    #         # if not start_stage_flag or not finish_stage_flag:
    #         #     raise exceptions.Warning(_("Please define a starting stage and ending stage for the stage set !"))
    #         # if multiple_start or multiple_ending:
    #         #     raise exceptions.Warning(_('You cannot define multiple start stages or multiple end stages !'))
    #     return super(StageSets, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(StageSets, self).write(vals)
    #     start_stage_flag = False
    #     multiple_start = False
    #     finish_stage_flag = False
    #     multiple_ending = False
    #     for i in self.stage_ids:
    #         try:
    #             if i.start_stage and not start_stage_flag:
    #                 start_stage_flag = True
    #             elif i.start_stage and start_stage_flag:
    #                 multiple_start = True
    #             if i.finish_stage and not finish_stage_flag:
    #                 finish_stage_flag = True
    #             elif i.finish_stage and finish_stage_flag:
    #                 multiple_ending = True
    #         except Exception as e:
    #             pass
    #     # if not start_stage_flag or not finish_stage_flag:
    #     #     raise exceptions.Warning(_("Please define a starting stage and ending stage for the stage set !"))
    #     # if multiple_start or multiple_ending:
    #     #     raise exceptions.Warning(_('You cannot define multiple start stages or multiple end stages !'))
    #     return res


class SelectedStages(models.Model):
    _name = 'selected.stages'
    _order = 'sequence ASC'

    sequence = fields.Integer()
    stage_set = fields.Many2one(
            'fsm.stage.sets',
            string="Stage Set"
    )
    stage_id = fields.Many2one(
            'fsm.stages',
            string="State",
            required=True
    )
    # conditions to change state
    conditions = fields.Text(
            string="Conditions"
    )
    # roles, who can change state
    role_everyone = fields.Boolean(
            string="Everyone",
            help="Allows anyone to change the state"
    )
    role_admin = fields.Boolean(
            string="Admin",
            default=True,
            help="Admin can change stage"
    )
    role_manager = fields.Boolean(
            string="Manager",
            help="FSM Manager can change stage"
    )
    role_team_lead = fields.Boolean(
            string="Team Leader",
            help="Assigne team lead can change stage"
    )
    role_emp = fields.Boolean(
            string="Employee",
            help="Members of assigned "
                 "teams can change stage"
    )

    # we need to specify the stage where the work starts,
    #  to automatically start the related workitem
    start_stage = fields.Boolean(
            string="Staring stage"
    )
    finish_stage = fields.Boolean(
            string="Final stage"
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
