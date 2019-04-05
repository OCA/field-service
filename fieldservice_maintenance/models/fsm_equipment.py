# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'

    maintenance_equipment_id = fields.Many2one(
        'maintenance.equipment', string='Related Maintenance Equipment',
        required=True, ondelete='restrict', delegate=True, auto_join=True,
        index=True)

    @api.model
    def create(self, vals):
        maintenance_equipment_id = self.env['maintenance.equipment'].create({
            'name': vals.get('name'),
            'equipment_assign_to': 'other',
            'is_fsm_equipment': True,
            'note': vals.get('notes', False),
            'serial_no':
                vals['lot_id'] and
                self.env['stock.production.lot'].browse(vals['lot_id']).name
                or False})
        if maintenance_equipment_id:
            vals.update({
                'maintenance_equipment_id': maintenance_equipment_id.id})
        return super(FSMEquipment, self).create(vals)
