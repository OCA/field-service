# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo import api, fields, models, _


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    fsm_order_id = fields.Many2one('fsm.order', 'Field Service Order')

    @api.model
    def create(self, vals):
        # create FSM order with type maintenance if selected equipment is
        # enabled with boolean is_fsm_equipment
        request = super(MaintenanceRequest, self).create(vals)
        ctx = dict(self._context)
        if request.equipment_id.is_fsm_equipment and "fsm_order" not in ctx:
            # Get the fsm equipment
            fsm_equipment = self.env['fsm.equipment'].search(
                [('maintenance_equipment_id', '=', request.equipment_id.id)],
                limit=1)
            fsm_order_type = self.env['fsm.order.type'].search(
                [('internal_type', '=', 'maintenance')],
                order="id desc", limit=1)
            if not fsm_equipment.current_location_id.id:
                raise UserError(_(
                    'Missing current location on FSM equipment %s')
                    % fsm_equipment.name)
            fsm_order_id = self.env['fsm.order'].create(
                {'type': fsm_order_type.id,
                 'equipment_id': fsm_equipment.id,
                 'location_id': fsm_equipment.current_location_id.id,
                 'request_id': request.id,
                 'description': request.description,
                 'scheduled_date_start': request.schedule_date,
                 'scheduled_duration': request.duration
                 })
            request.fsm_order_id = fsm_order_id
        return request
