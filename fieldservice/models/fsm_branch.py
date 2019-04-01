# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMBranch(models.Model):
    _name = 'fsm.branch'
    _description = 'branch'

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Branch Manager')
    district_id = fields.Many2one('fsm.district', string='District')
    description = fields.Char(string='Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)
