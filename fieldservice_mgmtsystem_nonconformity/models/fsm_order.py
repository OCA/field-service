# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmOrder(models.Model):

    _inherit = 'fsm.order'

    mgmtsystem_nonconformity_ids = fields.One2many(
        'mgmtsystem.nonconformity',
        'fsm_order_id',
        string="Non-Conformities"
    )

    mgmtsystem_nonconformity_count = fields.Integer(
        compute='_compute_mgmtsystem_nonconformity_count',
        string='# Non-Conformities'
    )

    @api.depends('mgmtsystem_nonconformity_ids')
    def _compute_mgmtsystem_nonconformity_count(self):
        for fsm_order in self:
            fsm_order.mgmtsystem_nonconformity_count = len(
                fsm_order.mgmtsystem_nonconformity_ids)
