# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMVehicle(models.Model):
    _name = 'fsm.vehicle'
    _description = 'Field Service Vehicle'

    name = fields.Char(string='Name', required='True')
    fsm_person_id = fields.Many2one('fsm.person', string='Assigned Driver')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Vehicle name already exists!"),
    ]
