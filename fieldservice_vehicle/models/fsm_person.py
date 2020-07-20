# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    vehicle_id = fields.Many2one("fsm.vehicle", string="Default Vehicle")
