# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMVehicle(models.Model):
    _name = 'fsm.vehicle'
    _description = 'Field Service Vehicle'

    name = fields.Char(string='Name', required='True')
    person_id = fields.Many2one('fsm.person', string='Assigned Driver')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Vehicle name already exists!"),
    ]
