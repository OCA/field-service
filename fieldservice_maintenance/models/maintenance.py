# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    is_fsm_equipment = fields.Boolean(string='Is a FSM Equipment')


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    fsm_order_id = fields.Many2one('fsm.order', 'Field Service Order')

    @api.model
    def create(self, vals):
        # create FSM order with type maintenance if selected equipment is
        # enabled with boolean is_fsm_equipment
        request = super(MaintenanceRequest, self).create(vals)
        if request.equipment_id.is_fsm_equipment:
            # Get the fsm equipment
            fsm_equipment = self.env['fsm.equipment'].search(
                'maintenance_equipment_id', '=', request.equipment_id)
            fsm_order_id = self.env['fsm.order'].create({
                'type': 'maintenance',
                'equipment_id': fsm_equipment and fsm_equipment[0].id or False
                })
            request.fsm_order_id = fsm_order_id
        return request
