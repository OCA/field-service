from odoo import api, exceptions, fields, models, _


class WorkItemFSM(models.Model):
    _name = 'fsm.work_item'
    _description = 'Work-item'

    # making the name, unique
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Item name already exists !"),
    ]

    name = fields.Char(string='Name', required=True)
    work_set_id = fields.Many2one('fsm.work_set',
                                  string="Work-set")
    # skills needed for this work_item
    skill_sets = fields.Many2one('fsm.skills',
                                 string="Needed Skill")

    description = fields.Text(string='Description')
    item_target = fields.One2many('work_item.target',
                                  'work_item_id',
                                  string="Item Target")

    quality_level = fields.Selection([('1', '1'),
                                      ('2', '2'),
                                      ('3', '3')],
                                     default="1",
                                     string="Quality Level")
    team_id = fields.Many2one('fsm.teams',
                              string="Team")
    person_ids = fields.Many2many('fsm.person',
                                  string="Employees")
    status = fields.Selection([('draft', 'Draft'),
                               ('ongoing', 'Ongoing'),
                               ('done', 'Done')],
                              string="Status",
                              default='draft')
    final_cost = fields.Float(string="Final Cost",
                              default=0)
    hours_spent = fields.Float(string="Hours Spent",
                               default=1)
    price_categ = fields.Selection([('low', 'Low'),
                                    ('medium', 'Medium'),
                                    ('high', 'High')],
                                   string="Price Category")
    hourly_cost = fields.Float(string="Hourly Cost")
    employees_needed = fields.Integer(string="No. of employees needed",
                                      default=1)
    available_emp = fields.Char(compute='compute_available_emp_count')
    undermanned = fields.Boolean(string="Can be undermanned ",
                                 default=True)

    # we don't need to auto start the job again ,
    #  which we reset manually after it is started once
    prevent_auto_start = fields.Boolean(default=False, store=True)
    next_job_id = fields.Many2one('fsm.work_item',
                                  string="Next Work Item")

    @api.depends('team_id')
    def compute_available_emp_count(self):
        """We are setting the number of
        available employees of the selected team from this function."""
        if not self.team_id:
            self.available_emp = None
        elif self.team_id:
            emp_count = len(self.team_id.team_members)
            emp_avail = 0
            for i in self.team_id.team_members:
                if i.name.available:
                    emp_avail += 1
            self.available_emp = \
                str(emp_avail) + "/" + str(emp_count) + " Employees " \
                                                        "available."

    @api.onchange('price_categ', 'work_set_id')
    def _find_price_categ(self):
        """We are setting the hourly cost based on the selected skill
        and the price category. Even though the hourly cost is
        auto filled, it is still editable."""
        if not self.price_categ:
            self.price_categ =\
                self.work_set_id.price_categ if self.work_set_id else None
        hourly_cost = 0
        if self.price_categ and self.skill_sets:
            categ_price = self.env['service.categ.price']
            categ = \
                categ_price.search([('skill_id', '=', self.skill_sets.id),
                                    ('name', '=', self.price_categ.title())
                                    ], limit=1)
            hourly_cost += categ and categ.cost or 0
        self.hourly_cost = hourly_cost
        domain = None
        if self.work_set_id:
            team_ids = [i.team_id.id for i in self.work_set_id.team_id]
            domain = [('id', 'in', team_ids)]
        return {
            'domain': {
                'team_id': domain
            }
        }

    @api.onchange('team_id')
    def onchange_team(self):
        """
        We need to check whether any of the members
        of the selected team is currently involved in any
        ongoing works, if yes, we will raise a warning.
        Employee can be part of only one work at a time.

        :return: domain for the field employees,
        so that it will show only those employees
        in the selected teams.
        """
        domain = []
        if self.team_id:
            self.person_ids = None
            team_ids = self.team_id.ids
            members = []
            cr = self._cr
            if team_ids:
                cr.execute("SELECT name "
                           "FROM fsm_team_member "
                           "WHERE team_id IN %s",
                           (tuple(team_ids), ))
                result = cr.fetchall()
                members = [i[0] for i in result]
            domain = "[('id', 'in', " + str(members) + ")]"
        return {
            'domain': {
                'person_ids': domain
            }
        }

    @api.onchange('skill_sets')
    def onchange_skill_sets(self):
        """skill_id
        We will be setting the teams list based on the needed skills.
        We need to show only those teams with 'ANY OF THE' specified skills.
        :return:
        """
        domain = []
        team_list = []
        if self.skill_sets:
            self.team_id = None
            self.person_ids = None
            skill_ids = self.skill_sets.ids
            all_teams = self.env['fsm.teams'].search([])
            for team in all_teams:
                for i in skill_ids:
                    if i in team.basic_skills.ids:
                        team_list.append(team.id)\
                            if team.id not in team_list else None
            domain = "[('id', 'in'," + str(team_list) + ")]"
        return {
            'domain': {
                'team_id': domain
            }
        }

    @api.multi
    def write(self, vals):
        result = super(WorkItemFSM, self).write(vals)

        if self.status == 'ongoing':
            # checking whether this work has the needed
            # number of employees or not
            if not self.undermanned:
                if self.employees_needed > len(self.person_ids):
                    raise exceptions.Warning(_("Employees requirement "
                                               "is not satisfied."))

            # a team is selected
            team = self.team_id
            person_ids = self.person_ids
            res = self.search([
                ('team_id', '=', team.id),
                ('status', '=', 'ongoing'),
                ('id', '!=', self.id)
            ])
            if res and person_ids:
                # checking whether any of the selected employee is included
                # for any other work-items
                raise_warning = False
                emp_names = ''
                for item in res:
                    for emp in person_ids:
                        if emp.id in item.person_ids.ids:
                            # raise a warning
                            self.person_ids = None
                            raise_warning = True
                            emp_names += str(emp.name) + ', '
                if raise_warning:
                    raise exceptions.Warning(_("%s  have another job "
                                               "ongoing now !") %
                                             (emp_names[:-2]))
            # it is an ongoing job, so the employees are not available
            for person in self.person_ids:
                person.available = False
        if self.status in ['draft', 'done']:
            # not ongoing job, so the employees are available
            for employee in self.person_ids:
                employee.available = True
            # we need to start the next job automatically
            items = self.work_set_id.work_item_ids
            for j in range(0, len(items)):
                if items[j].id == self.id and j + 1 < len(items):
                    items[j+1].status = 'ongoing'
                    break

        if vals.get('work_set_id'):
            rec_id = vals.get('work_set_id')
            rec = self.env['fsm.work_set'].browse(rec_id)
            self.price_categ = rec.price_categ
        return result

    @api.model
    def create(self, vals):
        res = super(WorkItemFSM, self).create(vals)

        # checking employee status
        if res.status == 'ongoing':
            team = res.team_id
            employees = res.person_ids.ids
            rec = self.search([
                ('team_id', '=', team.id),
                ('status', '=', 'ongoing'), ('id', '!=', res.id)
            ])
            if rec and employees:
                # checking whether any of the selected employee is included
                # for any other work-items
                for item in rec:
                    for emp in employees:
                        if emp in item.person_ids.ids:
                            # raise a warning
                            res.person_ids = None
                            raise exceptions.Warning(_("Employees cannot have"
                                                       " more than one "
                                                       "job at a time!"))
            # it is an ongoing job, so the employees are not available
            for employee in res.person_ids:
                employee.available = False
        if res.status in ['draft', 'done']:
            # not ongoing job, so the employees are available
            for employee in res.person_ids:
                employee.available = True

        if vals.get('work_set_id'):
            rec_id = vals.get('work_set_id')
            rec = self.env['fsm.work_set'].browse(rec_id)
            res.price_categ = rec.price_categ
        return res

    @api.model
    def action_open_workitems(self):
        """Opens the workitems based on the signed in user"""
        user = self.env.user
        person_obj = self.env['fsm.person']
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
                # selecting the teams where this employee is the leader
                #  or member
                teams = user.fsm_team_ids and user.fsm_team_ids.ids or []

                domain = "[('team_id', 'in', " + str(teams) + ")]"
            elif employees and user.has_group('fieldservice.group_fsm_user'):
                # case: employee
                # selecting all the teams this employee is member of
                teams = []
                for team in user.fsm_team_ids:
                    for j in team.team_members:
                        if j.name.id in employees.ids:
                            teams.append(team.id) \
                                if team.id not in teams else None
                domain = "[('team_id', 'in', " + str(teams) + ")]"
            elif not employees:
                domain = "[('team_id', 'in', " + str([]) + ")]"
        return {
            'name': 'Work-Items',
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.work_item',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'tree_view_ref': 'fsm_task_handler.fsm_work_item_tree',
                'form_view_ref': 'fsm_task_handler.fsm_work_item_form',
            }
        }

    def compute_final_cost(self):
        """
        We will find the total cost required for this workitem.
        We will be checking for the team assigned
         to this item(team or employees)
        and cost of target items and number of hours worked
        for each employees
        """
        # cost for item-targets
        target_cost = 0
        for rec in self.item_target:
            target_cost += rec.quantity * rec.unit_price
        # total hours spent
        hours_spent = self.hours_spent or 1
        # need to find the number of employees involved
        # if any employees are selected, we will take the number
        #  of employees selected
        # otherwise, we will select the number of employees
        #  in the team selected
        emp_count = 0
        if self.person_ids:
            emp_count += len(self.person_ids)
        elif self.team_id:
            emp_count += len(self.team_id.team_members)
        else:
            raise exceptions.UserError(_('Please select a team '
                                         'or employee first !'))
        if emp_count == 0:
            raise exceptions.UserError(_('No employees are'
                                         ' assigned to this workitem !'))

        # finding cost needed for the service,
        #  i.e, hours_spent * hourly cost of service
        service_hourly_cost = 0
        if self.hourly_cost:
            service_hourly_cost += self.hourly_cost

        final_cost = \
            (hours_spent * service_hourly_cost * emp_count) + target_cost
        self.final_cost = final_cost
        return False

    @api.multi
    def start_job(self):
        """To start the job"""
        for rec in self:
            if rec.work_set_id.work_started_flag != 'started':
                raise exceptions.UserError(_('Parent'
                                             ' work-set is not started !'))
            rec.status = 'ongoing'

    @api.multi
    def finish_job(self):
        """To finish the job"""
        for rec in self:
            rec.status = 'done'
            # -after finishing the job, we have to
            # start the next job immediatly
            # for that, we are checking the parent workset is started or not
            # we will start the job only if the workset is started
            if rec.next_job_id and rec.next_job_id.work_set_id:
                if rec.next_job_id.work_set_id.work_started_flag == 'started':
                    rec.status = 'ongoing'

    @api.multi
    def reset_to_draft(self):
        """Resets to draft"""
        for job in self:
            job.status = 'draft'


class ItemTargets(models.Model):
    _name = 'work_item.target'
    _rec_name = 'product_id'

    work_item_id = fields.Many2one('fsm.work_item',
                                   string="Work-Item")
    product_id = fields.Many2one('product.product',
                                 string="Item")
    quantity = fields.Float(string="Quantity",
                            default=1)
    unit_price = fields.Float(string="Unit Price(Per hour)",
                              default=0)


class ServiceCategPrice(models.Model):
    """Model for category-wise service price."""
    _name = 'service.categ.price'

    skill_id = fields.Many2one('fsm.skills')


class PersonWorkItem(models.Model):
    _inherit = 'fsm.person'

    def open_related_tasks(self):
        """Opens related work items, this user is involved in"""
        return self.env['fsm.work_item'].action_open_workitems()
