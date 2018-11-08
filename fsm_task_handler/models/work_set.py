import logging

from odoo import api, exceptions, fields, models, _
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class WorksetTeamRelation(models.Model):
    _name = 'workset.fsm.teams'

    workset_id = fields.Many2one('fsm.work_set',
                                 string="Workset")
    team_id = fields.Many2one('fsm.teams',
                              string="Team")


class WorkSetsFSM(models.Model):
    _name = 'fsm.work_set'
    _inherit = 'mail.thread'
    _description = 'Work-set'

    # making the name, unique
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Work-Set name already exists !"),
    ]

    def _default_stage_set(self):
        """Setting default stage"""
        rec = self.env['fsm.stage.sets'].search([], limit=1)
        return rec.id if rec else None

    name = fields.Char(string='Name',
                       required=True)
    work_order_id = fields.Many2one('fsm.order',
                                    string="Work-order")

    description = fields.Text(string='Description')

    work_set_forms = fields.One2many('work_set.form',
                                     'work_set_id',
                                     string="Questionnaires")
    work_set_answers = fields.One2many('work_set.answers',
                                       'work_set_id',
                                       string="Answers")
    price_categ = fields.Selection([('low', 'Low'),
                                    ('medium', 'Medium'),
                                    ('high', 'High')],
                                   string="Price Category")
    stage_set = fields.Many2one('fsm.stage.sets',
                                default=lambda self: self._default_stage_set(),
                                string="Stage Set",
                                required=True)
    # just a dummy field to show the stages list
    fsm_stage_list = fields.Char(string="Stages", readonly=1)
    stage_id = fields.Many2one('fsm.stages',
                               string='Stage',
                               store=True)
    color = fields.Integer('Color Index',
                           default=0)
    state = fields.Char(string="State")
    team_id = fields.One2many('workset.fsm.teams',
                              'workset_id',
                              string="Teams")
    customer_id = fields.Many2one('res.partner',
                                  domain="[('customer', '=', True)]",
                                  string="Customer",
                                  related='work_order_id.customer_id',
                                  track_visibility='onchange')
    question_categ = fields.One2many('question.category',
                                     'work_set_id')
    reject_reason = fields.Text(string="Reason",
                                help="Provide a short note"
                                     " on proposal rejection",
                                track_visibility='onchange')
    # a flag to specify the work order status, whether it is started or not
    work_started_flag = fields.Char(string="Work Started",
                                    default="False")
    work_item_ids = fields.One2many('fsm.work_item',
                                    'work_set_id',
                                    string="FSM Work-Item")

    @api.multi
    def write(self, vals):
        """
        This is where we are creating the
        questions related to the selected surveys.
        This will be executed when we modify
        an existing record.
        """
        res = super(WorkSetsFSM, self).write(vals)
        if vals.get('work_set_forms'):
            for rec in vals.get('work_set_forms'):
                if rec[2]:
                    survey_id = rec[2].get('name')
                    for question in\
                            self.env['product.survey'].browse(survey_id):
                        self.write({
                            'work_set_answers': [(0, 0, {
                                'name': question.name,
                                'work_set_id': self.id,
                                'survey_id': survey_id
                            })]
                        })
        if vals.get('stage_set'):
            temp_stage_set = \
                self.stage_set.stage_ids.sorted(key=lambda r: r.sequence)[0]
            stage = temp_stage_set.stage_id if temp_stage_set else None

            if stage:
                self.stage_id = stage.id
        return res

    @api.model
    def create(self, vals):
        """
        We are setting the questions for
        the related surveys here. This will be executed when we
        create new records.
        """
        res = super(WorkSetsFSM, self).create(vals)
        if vals.get('work_set_forms'):
            for rec in vals.get('work_set_forms'):
                if rec[2]:
                    survey_id = rec[2].get('name')
                    for question in\
                            self.env['product.survey'].browse(survey_id):
                        res.write({
                            'work_set_answers': [(0, 0, {
                                'name': question.name,
                                'work_set_id': self.id,
                                'survey_id': survey_id
                            })]
                        })
        if vals.get('stage_set'):
            temp_stage_set = \
                res.stage_set.stage_ids.sorted(key=lambda r: r.sequence)[0]
            stage = temp_stage_set.stage_id if temp_stage_set else None

            if stage:
                res.stage_id = stage.id
        return res

    @api.model
    def action_open_worksets(self):
        """Opens the work-sets based on the signed in user"""
        user = self.env.user
        cr = self._cr
        person_obj = self.env['fsm.person']
        # here the employees refers to the person who are assigned the job
        employees = \
            person_obj.search([('partner_id', '=', user.partner_id.id)]) or []
        if user.id == 1:
            # admin should see all the records
            # setting domain to empty
            domain = []
        else:
            # the signed in user is not admin
            # so we need to check his privileages
            if user.has_group('fieldservice.group_fsm_manager'):
                # this user is a manager
                # selecting all the items

                domain = []

            elif employees and \
                    user.has_group('fieldservice.group_fsm_dispatcher'):
                # case: team leader
                # selecting the teams where
                # this employee/person is the leader or member
                if user.fsm_team_ids:
                    teams = user.fsm_team_ids.ids
                else:
                    teams = []

                ids = []
                if teams:
                    cr.execute("SELECT workset_id "
                               "FROM workset_fsm_teams "
                               " WHERE team_id IN %s", (tuple(teams), ))
                    ids = [i[0] for i in cr.fetchall()]

                domain = "[('id', 'in', " + str(ids) + ")]"
            elif employees and user.has_group('fieldservice.group_fsm_user'):
                # case: employee
                # selecting all the teams this employee is member of
                teams = []
                for team in user.fsm_team_ids:
                    for j in team.team_members:
                        if j.name.id in employees.ids:
                            teams.append(team.id) if\
                                team.id not in teams else None
                ids = []
                if teams:
                    cr.execute("SELECT workset_id "
                               "FROM workset_fsm_teams "
                               "WHERE team_id IN %s",
                               (tuple(teams),))
                    ids = [i[0] for i in cr.fetchall()]

                domain = "[('id', 'in', " + str(ids) + ")]"
            elif not employees:
                domain = "[('id', 'in', " + str([]) + ")]"
        return {
            'name': 'Work-Sets',
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.work_set',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'tree_view_ref': 'fsm_task_handler.fsm_work_sets_tree',
                'form_view_ref': 'fsm_task_handler.fsm_work_sets_form',
            }
        }

    def approve_operation(self):
        """Approves the proposal assigned to the person"""
        stage_id = self.env['fsm.stages'].search([('name', '=', 'Approved')],
                                                 limit=1)
        if not stage_id:
            stage_id = self.env['fsm.stages'].create({'name': 'Approved'})
        self.stage_id = stage_id.id
        self.state = stage_id.name
        return False

    def reject_operation(self):
        """Rejects the proposal assigned to the person"""
        stage_id = self.env['fsm.stages'].search([('name', '=', 'Rejected')],
                                                 limit=1)
        if not stage_id:
            stage_id = self.env['fsm.stages'].create({'name': 'Rejected'})
        self.stage_id = stage_id.id
        self.state = stage_id.name
        return False

    @api.model
    def fetch_stages_list(self, stage_set):
        if not stage_set:
            return []
        cr = self._cr
        cr.execute("SELECT fs.id, fs.name "
                   "FROM selected_stages ss "
                   "JOIN fsm_stages fs ON(ss.stage_id=fs.id) "
                   "WHERE ss.stage_set=%s",
                   (stage_set, ))
        res = cr.dictfetchall()
        return res

    @api.model
    def stage_transition(self, rec_id, stage, stage_name):
        """Changes stage after the validations.
        :rec_id: id of the current record(workset, or order),
        :stage: id of stage to which we are intended to move,
        :stage_name: name of the stage to which we are intended to move
        """
        rec = self.search([('id', '=', int(rec_id))])
        if not rec:
            return

        stage = int(stage)
        stage_set = rec.stage_set
        stage_selected = None
        user = self.env.user
        current_stage = None
        for rec_set in stage_set.stage_ids:
            if rec_set.stage_id.id == stage:
                stage_selected = rec_set
            if rec_set.stage_id.id == rec.stage_id.id:
                current_stage = rec_set

        #  ---------ADVANCED TRANSITIONS --------START
        # This advanced transitions section defines the stages
        # to which we are  allowed to move records into.
        # so we will be checking that the current user is
        #  allowed to change records
        #  from the previous stage to the new one.
        if current_stage.use_trasitions and current_stage.transition_ids:
            # does have advanced transition rules
            transition_lines = current_stage.transition_ids
            selected_trans = None
            for line in transition_lines:
                if line.dest_stage.id == stage:
                    selected_trans = line
                    break
            # if there are no transition rules defined for the
            # new stage from the current stage, we won't
            # perform the validations and allow the transitions
            if selected_trans:
                # there is a transition rule defined
                #  for the new stage from the current stage
                # ---------VERIFY STAGE TRANSITION AUTHORITY ----START
                has_permission = False
                for trans in selected_trans.transition_allowed:
                    if trans.name == 'Everyone':
                        # anyone can change state
                        has_permission = True
                    elif trans.name == 'Admin':
                        # only admin is allowed to change
                        if user.id == 1:
                            has_permission = True
                    elif trans.name == 'Manager':
                        # fsm manager has permission
                        if user.has_group('fieldservice.group_fsm_manager'):
                            has_permission = True
                    elif trans.name == 'Team Leader':
                        # fsm dispatcher(team lead) has permission
                        # in this case, the leaders of the assigned team
                        #  can change state
                        if user.has_group('fieldservice.group_fsm_dispatcher'):
                            # collecting the teams assigned to
                            # this record(work order / work set)
                            rec_team_ids = [i.team_id.id for i in rec.team_id]
                            # fetching current user's teams
                            user_team_ids = self.find_user_teams()
                            if rec_team_ids and user_team_ids:
                                # one or more teams assigned to this record
                                # and this user has some teams
                                for u_team in user_team_ids:
                                    if u_team in rec_team_ids:
                                        # current user is a dispatcher
                                        # and is member of one of the
                                        # teams assigned
                                        #  to the current record
                                        has_permission = True
                                        break

                    elif trans.name == 'Person':
                        # fsm employee has permission
                        if user.has_group('fieldservice.group_fsm_user'):
                            has_permission = True

                if not has_permission:
                    raise exceptions.UserError(_("You don't have permission "
                                                 "to perform this operation."))
                _logger.info("This user does have permission"
                             " to change to this stag    e")

                # --------VERIFY STAGE TRANSITION AUTHORITY ----END

                # --------VERIFY CONDITIONS ---------START
                validation_success = True
                if selected_trans.validate_transition:
                    # condition is set
                    try:
                        result = safe_eval(selected_trans.validate_transition)
                        if result:
                            validation_success = \
                                self.validate_conditions(result)
                        else:
                            validation_success = False
                    except:
                        raise exceptions.Warning(_('Could not verify '
                                                   'the conditions specified '
                                                   'for this stage, please '
                                                   'configure it properly !'))
                    if not validation_success:
                        raise exceptions.Warning(_('Some conditions are '
                                                   'not met, you cannot '
                                                   'change the state !\n'
                                                   'Please check the '
                                                   'conditions '
                                                   'associated with '
                                                   'this stage.'))
                # --------VERIFY CONDITIONS ---------END

        # ---------ADVANCED TRANSITIONS -------- END

        # ---------NORMAL TRANSITIONS -------- start
        # in this section, we will check that
        # the current user is allowed to move
        # records into the new stage or not.
        validation_success = True
        has_permission = False
        # ---------VERIFY STAGE TRANSITION AUTHORITY ----START
        if not stage_selected:
            return
        if stage_selected.role_everyone:
            # anyone can change state
            has_permission = True
        elif stage_selected.role_admin:
            # only admin is allowed to change
            if user.id == 1:
                has_permission = True
        elif stage_selected.role_manager:
            # fsm manager has permission
            if user.has_group('fieldservice.group_fsm_manager'):
                has_permission = True
        elif stage_selected.role_team_lead:
            # fsm dispatcher(team lead) has permission
            # in this case, the leaders of the assigned team can change state
            if user.has_group('fieldservice.group_fsm_dispatcher'):
                # collecting the teams assigned to
                # this record(work order / work set)
                rec_team_ids = [i.team_id.id for i in rec.team_id]
                # fetching current user's teams
                user_team_ids = self.find_user_teams()
                if rec_team_ids and user_team_ids:
                    # one or more teams assigned to this record
                    # and this user has some teams
                    for u_team in user_team_ids:
                        if u_team in rec_team_ids:
                            # current user is a dispatcher
                            # and is member of one of the teams assigned
                            #  to the current record
                            has_permission = True
                            break

        elif stage_selected.role_emp:
            # fsm employee has permission
            if user.has_group('fieldservice.group_fsm_user'):
                has_permission = True

        if not has_permission:
            raise exceptions.UserError(_("You don't have permission "
                                         "to perform this operation."))

        _logger.info("This user does have permission"
                     " to change to this stage")

        # ---------VERIFY STAGE TRANSITION AUTHORITY ----END

        # --------VERIFY CONDITIONS ---------START
        if stage_selected.conditions:
            # condition is set
            try:
                result = safe_eval(stage_selected.conditions)
                validation_success = \
                    self.validate_conditions(result) if result else False
            except:
                raise exceptions.Warning(_('Could not verify '
                                           'the conditions specified '
                                           'for this stage, please '
                                           'configure it properly !'))
            if not validation_success:
                raise exceptions.Warning(_('Some conditions are '
                                           'not met, you cannot '
                                           'change the state !\n'
                                           'Please check the conditions '
                                           'associated with this stage.'))
        # --------VERIFY CONDITIONS ---------END

        # ---------NORMAL TRANSITIONS -------- end

        # if has_permission and validation_success:
        rec.write({
            'stage_id': stage,
            'state': stage_name
        })

    def validate_conditions(self, result):
        """We will loop through all the conditions provided"""
        try:
            ready_to_move = False
            new_expression = []
            for exp in result:
                if type(exp) is tuple:
                    exp_list = list(exp)
                    field_name = exp_list
                    exp_list[0] = \
                        field_name[0].replace('parent_id', 'work_order_id')
                    exp_list[0] = field_name[0].replace('self.', '')
                    new_expression.append(tuple(exp_list))
                else:
                    new_expression.append(exp)

            for i in self.search(new_expression):
                if i.id == self.id:
                    ready_to_move = True
                    break
        except Exception as e:
            _logger.info('error occured while evaluating the conditions !')

        return ready_to_move

    def find_user_teams(self):
        """fetching current user's teams"""
        user = self.env.user
        if user.fsm_team_ids:
            return user.fsm_team_ids.ids
        else:
            return []
