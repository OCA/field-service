# Copyright (C) 2018 Open Source Integrators
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
        lot_id = vals.get('lot_id', False)
        if not vals.get('maintenance_equipment_id', False):
            maintenance_equipment_id = \
                self.env['maintenance.equipment'].create({
                    'name': vals.get('name'),
                    'is_fsm_equipment': True,
                    'note': vals.get('notes', False),
                    'serial_no':
                        lot_id and
                        self.env['stock.production.lot'].browse(lot_id).name,
                    'maintenance_team_id':
                        vals.get('maintenance_team_id', False) or
                        self.env.ref('maintenance.equipment_team_maintenance').
                        id})
            if maintenance_equipment_id:
                vals.update({
                    'maintenance_equipment_id': maintenance_equipment_id.id})
        return super().create(vals)

    @api.multi
    def unlink(self):
        equipments = self.mapped('maintenance_equipment_id')
        res = super(FSMEquipment, self).unlink()
        for equipment in equipments:
            other = self.env['fsm.equipment'].search(
                [('maintenance_equipment_id', '=', equipment.id)])
            if not other:
                equipment.is_fsm_equipment = False
        return res
