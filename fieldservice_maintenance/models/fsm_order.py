# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
# from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    type = fields.Selection(selection_add=[('maintenance', 'Maintenance')])
    request_id = fields.Many2one('maintenance.request',
                                 string='Maintenance Request')

    # @api.model
    # def create(self, vals):
    #     # if FSM order with type maintenance is create then
    #     # create maintenance request
    #     order = super(FSMOrder, self).create(vals)
    #     if order.type == 'maintenance':
    #         employee_rec = self.env['hr.employee'].search(
    #             [('user_id', '=', self.env.uid)], limit=1)
    #         if order.equipment_id and not order.request_id:
    #             equipment = order.equipment_id
    #             team_id = equipment.maintenance_equipment_id and\
    #                 equipment.maintenance_equipment_id.maintenance_team_id.id
    #             request_id = self.env['maintenance.request'].with_context(
    #                 fsm_order=True).create({
    #                     'name': order.name or '',
    #                     'employee_id': employee_rec.id,
    #                     'equipment_id':
    #                         equipment.maintenance_equipment_id.id,
    #                     'category_id': equipment.category_id.id,
    #                     'request_date': fields.Date.context_today(self),
    #                     'maintenance_type': 'corrective',
    #                     'maintenance_team_id': team_id,
    #                     'schedule_date': order.request_early,
    #                     'description': order.description
    #                 })
    #             order.request_id = request_id
    #     return order
