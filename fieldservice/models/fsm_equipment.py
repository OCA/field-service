# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class FSMEquipment(models.Model):
    _name = 'fsm.equipment'
    _description = 'Field Service Equipment'

    name = fields.Char(string='Name', required='True')
    person_id = fields.Many2one('fsm.person', string='Assigned Operator')
    location_id = fields.Many2one('fsm.location', string='Assigned Location')
    notes = fields.Text(string='Notes')
    territory_id = fields.Many2one('fsm.territory', string='Territory')
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one('fsm.district', string='District')
    region_id = fields.Many2one('fsm.region', string='Region')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Equipment name already exists!"),
    ]

    @api.onchange('location_id')
    def _onchange_location_id(self):
        self.territory_id = self.location_id.territory_id

    @api.onchange('territory_id')
    def _onchange_territory_id(self):
        self.branch_id = self.territory_id.branch_id

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        self.district_id = self.branch_id.district_id

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.region_id = self.district_id.region_id
