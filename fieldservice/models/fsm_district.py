# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMDistrict(models.Model):
    _name = 'fsm.district'
    _description = 'District'

    name = fields.Char(string='Name', required=True)
    region_id = fields.Many2one('fsm.region', string='Region')
    partner_id = fields.Many2one('res.partner', string='District Manager')
    description = fields.Char(string='Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)
