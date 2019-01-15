# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    equipment_count = fields.Integer('# Equipments',
                                     compute='_compute_equipment_count')

    @api.multi
    def _compute_equipment_count(self):
        data = self.env['fsm.equipment'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
        count_data = dict((item['agreement_id'][0],
                           item['agreement_id_count']) for item in data)
        for agreement in self:
            agreement.equipment_count = count_data.get(agreement.id, 0)
