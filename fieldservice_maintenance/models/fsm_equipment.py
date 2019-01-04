# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'
    _inherits = {'maintenance.equipment': 'maintenance_equipment_id'}
    _description = 'FSM Maintenance equipment'

    maintenance_equipment_id = fields.Many2one(
        'maintenance.equipment', string='Maintenance Equipment', required=True,
        ondelete='restrict', delegate=True, auto_join=True)
