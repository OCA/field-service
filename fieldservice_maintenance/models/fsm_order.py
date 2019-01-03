# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.base_geoengine import geo_model


class FSMOrder(geo_model.GeoModel):
    _inherit = 'fsm.order'
    _description = 'Field Service Order Maintenance'

    type = fields.Selection(selection_add=[('maintenance', 'Maintenance')])
    request_id = fields.Many2one(
        'maintenance.request', 'Maintenance Request')

    @api.model
    def create(self, vals):
        # if FSM order with type maintenance is create then
        # create maintenance request
        order = super(FSMOrder, self).create(vals)
        if order.type == 'maintenance':
            employee_ids = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)])
            if employee_ids:
                employee_id = employee_ids[0]
            if order.equipment_id:
                equipment = order.equipment_id
                request_id = self.env['maintenance.request'].create({
                    'name': order.name or '',
                    'employee_id': employee_id.id,
                    'equipment_id':
                        equipment.maintenance_equipment_id
                        and equipment.maintenance_equipment_id.id or False,
                    'category_id':
                        equipment.category_id and
                        equipment.category_id.id or False,
                    'request_date': fields.Date.context_today(self),
                    'maintenance_type': 'corrective',
                    'maintenance_team_id':
                        equipment.maintenance_equipment_id and
                        equipment.maintenance_equipment_id.maintenance_team_id
                        and
                        equipment.maintenance_equipment_id.maintenance_team_id.id
                        or False,
                    'schedule_date': order.request_early,
                    'description': order.description
                })
                order.request_id = request_id
        return order
