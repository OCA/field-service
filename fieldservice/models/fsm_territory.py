# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
# from odoo.addons.base_geoengine import geo_model


class FSMTerritory(models.Model):
    _name = 'fsm.territory'
    _description = 'Territory'

    name = fields.Char(string='Name', required=True)
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one(related='branch_id.district_id',
                                  string='District')
    region_id = fields.Many2one(related='branch_id.district_id.region_id',
                                string='Region')

    person_ids = fields.Many2many('fsm.person', string='Field Service Workers')
    description = fields.Char(string='Description')
    person_id = fields.Many2one('fsm.person', string='Primary Assignment')
    type = fields.Selection([('zip', 'Zip'),
                             ('state', 'State'),
                             ('country', 'Country')], 'Type')

    zip_codes = fields.Char(string='ZIP Codes')
    state_ids = fields.One2many('res.country.state',
                                'territory_id', string='State Names')
    country_ids = fields.One2many('res.country',
                                  'territory_id',
                                  string='Country Names')


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    territory_ids = fields.Many2many('fsm.territory', string='Territories')


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    territory_id = fields.Many2one('fsm.territory', string='Territory')
