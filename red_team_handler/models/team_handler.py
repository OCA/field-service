# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


# model for fsm teams
class TeamsFSM(models.Model):
    _name = 'fsm.teams'

    name = fields.Char(
            string="Name",
            required=True
    )
    team_members = fields.One2many(
            'fsm.team.members',
            'team_id',
            string="Team Members"
    )
    basic_skills = fields.Many2many(
            'project.project',
            string="Basic Skills"
    )
    team_avail = fields.Selection([
        ('ordinary', 'Ordinary'),
        ('express', 'Express')],
            default='ordinary',
            string="Team Availability"
    )
    team_lead = fields.Many2one(
            'fsm.person',
            string="Team Leader",
            required=True
    )
    minimum_size = fields.Integer(
            string="Minimum-size",
            default=0
    )
    maximum_size = fields.Integer(
            string="Maximum-size",
            default=1
    )
    team_type = fields.Many2one(
            'team.type',
            string="Type"
    )

    # in order to handle the support tickets
    categ_list = fields.Many2many(
            'website.support.ticket.categories',
            string="Categories"
    )

    @api.multi
    def write(self, vals):
        if vals.get('team_lead') or\
                vals.get('team_members'):
            self.update_teams_list(vals)

        res = super(TeamsFSM, self).write(vals)
        if len(self.team_members) < self.minimum_size:
            # comparing the number of members
            # and maximum no. of members allowed
            raise exceptions.Warning(_("Minimum "
                                       "number of members"
                                       " not satisfied !"))
        if self.team_members and \
                        len(self.team_members) > self.maximum_size:
            # comparing the number of members
            # and maximum no. of members allowed
            raise exceptions.Warning(_("Maximum number"
                                       " of members exceeded !"))

        return res

    @api.model
    def create(self, vals):
        res = super(TeamsFSM, self).create(vals)
        if len(res.team_members) < res.minimum_size:
            # comparing the number of members and
            # maximum no. of members allowed
            raise exceptions.Warning(_("Minimum number"
                                       " of members not satisfied !"))
        if res.team_members and len(res.team_members) > res.maximum_size:
            # comparing the number of members
            # and maximum no. of members allowed
            raise exceptions.Warning(_("Maximum number"
                                       " of members exceeded !"))
        res.update_teams_list(vals)
        return res

    @api.model
    def action_open_teams(self):
        """Opens the teams based on the signed in user"""
        user = self.env.user

        persons = self.env['fsm.person'].search([
            ('user_id', '=', user.id)]) or []
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

            elif persons and \
                    user.has_group('fieldservice.group_fsm_dispatcher'):
                # case: team leader(dispatcher)
                # selecting the teams where
                # this employee is the leader or member
                teams = user.fsm_team_ids and\
                        user.fsm_team_ids.ids or []

                domain = "[('id', 'in', " + str(teams) + ")]"
            elif persons and user.has_group('fieldservice.group_fsm_user'):
                # case: member only
                # selecting all the teams this employee is member of
                teams = []
                for team in user.fsm_team_ids:
                    for j in team.team_members:
                        if j.name.id in persons.ids:
                            teams.append(team.id) if team.id not in teams else None

                domain = "[('id', 'in', " + str(teams) + ")]"
            elif not persons:
                domain = "[('id', 'in', " + str([]) + ")]"
        return {
            'name': 'FSM Teams',
            'type': 'ir.actions.act_window',
            'res_model': 'fsm.teams',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'tree_view_ref': 'red_team_handler.red_fsm_team_tree',
                'form_view_ref': 'red_team_handler.red_fsm_team_form',
            }
        }

    def update_teams_list(self, vals):
        """We will be updating the user's teams list here."""
        cr = self._cr
        user_obj = self.env['res.users']
        person_obj = self.env['fsm.person']
        if vals.get('team_lead'):
            old_person = self.team_lead
            old_user = user_obj.search([('partner_id', '=', old_person.partner_id.id)],
                                       limit=1)
            if old_user:
                # linked to a user
                # we need to remove old team lead's team
                if old_user.fsm_team_ids:
                    old_user.write({'fsm_team_ids': [(3, self.id)]})
            new_person = person_obj.browse(vals.get('team_lead'))
            new_user = user_obj.search([('partner_id', '=', new_person.partner_id.id)],
                                       limit=1)
            if new_user:
                # linked to a user
                new_user.write({'fsm_team_ids': [(4, self.id)]})\
                    if self.id not in new_user.fsm_team_ids.ids else None
        if vals.get('team_members'):
            for i in vals.get('team_members'):
                if i[2] and i[0] == 0:
                    # adding a new member
                    person = person_obj.browse(i[2].get('name'))
                    user = user_obj.search([('partner_id', '=', person.partner_id.id)],
                                           limit=1)
                    if user:
                        # linked to a user
                        user.write({
                            'fsm_team_ids': [(4, self.id)]
                        }) if self.id not in user.fsm_team_ids.ids else None
                elif i[0] == 2:
                    # removing existing member
                    cr.execute("SELECT name "
                               "FROM fsm_team_members "
                               "WHERE id=%s",
                               (i[1], ))
                    person_id = cr.fetchone()
                    person = person_id and person_obj.browse(person_id[0]) or None
                    user = user_obj.search([('partner_id', '=', person.partner_id.id)],
                                           limit=1)
                    if user:
                        # linked to a user
                        user and user.write({
                            'fsm_team_ids': [(3, self.id)]
                        })
                elif i[0] == 1:
                    # updating existing member
                    cr.execute("SELECT name "
                               "FROM fsm_team_members "
                               "WHERE id=%s",
                               (i[1],))
                    person_id = cr.fetchone()
                    person = person_id and person_obj.browse(person_id[0]) or None
                    user = user_obj.search([('partner_id', '=', person.partner_id.id)],
                                           limit=1)
                    if user:
                        # linked to a user
                        user and user.write({
                            'fsm_team_ids': [(3, self.id)]
                        })

                    new_person = person_obj.browse(i[2].get('name'))
                    new_user = user_obj.search([('partner_id', '=', new_person.partner_id.id)],
                                               limit=1)
                    if new_user:
                        # linked to a user
                        new_user and new_user.write({
                            'fsm_team_ids': [(4, self.id)]
                        })


class ProjectsModified(models.Model):
    _inherit = 'project.project'

    team_id = fields.Many2one(
            'fsm.teams',
            string="Team"
    )


class TeamTypeFSM(models.Model):
    _name = 'team.type'

    name = fields.Char(
            string="Type"
    )


class SupportTicketTeam(models.Model):
    _inherit = 'website.support.ticket'

    team_id = fields.Many2one(
            'fsm.teams',
            string="Assigned Team"
    )

    @api.onchange('category')
    def onchange_category(self):
        """We need to set a domain on teams,
        we need to show only those teams in the selected category"""
        domain = None
        if self.category:
            self.team_id = None
            teams_to_show = []
            teams = self.env['fsm.teams'].search([])
            for i in teams:
                if self.category.id in i.categ_list.ids:
                    teams_to_show.append(i.id)
            domain = "[('id', 'in', " + str(teams_to_show) + ")]"
        return {
            'domain': {
                'team_id': domain
            }
        }


class EmployeeFsmTeams(models.Model):
    _inherit = 'res.users'

    fsm_team_ids = fields.Many2many('fsm.teams', string="Teams")
