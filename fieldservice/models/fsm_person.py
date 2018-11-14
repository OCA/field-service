# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _description = 'Field Service Person'

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 delegate=True, auto_join=True)

    skills = fields.Many2many('fsm.skill', string='Skills')
    skill_level = fields.Many2many('hr.skill.level', string='Skill Level')

    category = fields.Many2many('fsm.category', string='Category')
    phone = fields.Char(string='Phone Number', size=11)
    email = fields.Char(string='Email Address')

    normal_rate = fields.Float(string='Normal Rate')

    after_hours_rate = fields.Float(string='After Hours Rate')
    emergency_rate = fields.Float(string='Emergency Rate')
    project_rate = fields.Float(string='Project Rate')
    travel_rate = fields.Float(string='Travel Rate')

    prefered_location = fields.Many2one('fsm.location',
                                    string='Prefered Location')

    sales_territory_id = fields.Many2one('fsm.territory', string='Territory')
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one('fsm.district', string='District')
    region_id = fields.Many2one('fsm.region', string='Region')

    @api.model
    def create(self, vals):
        vals.update({'fsm_person': True})
        return super(FSMPerson, self).create(vals)

    @api.onchange('skills')
    def oncahnge_skills(self):
        ids = []
        for skill in self.skills:
            ids.append(skill.id)

    @api.onchange('customer')
    def _getCustomerContacts(self):
        if self.skills:
            ids = []
            for skill_id in self.skills:
                ids.append(skill_id.id)
            domain = {
                        'skill_id': [('skill_id', 'in', ids)]
            }
        else:
            domain = {}
        return domain

    @api.onchange('sales_territory_id')
    def _onchange_territory_id(self):
        self.branch_id = self.sales_territory_id.branch_id

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        self.district_id = self.branch_id.district_id

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.region_id = self.district_id.region_id
