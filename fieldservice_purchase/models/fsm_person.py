# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    pricelist_count = fields.Integer(
        compute='_compute_pricelist_count',
        string='# Pricelists'
    )

    @api.multi
    def _compute_pricelist_count(self):
        for worker in self:
            worker.pricelist_count = self.env['product.supplierinfo'].\
                search_count([('name', '=', worker.partner_id.id)])

    @api.multi
    def action_view_pricelists(self):
        for worker in self:
            pricelist = self.env['product.supplierinfo'].search(
                [('name', '=', worker.partner_id.id)])
            action = self.env.ref(
                'product.product_supplierinfo_type_action').read()[0]
            if len(pricelist) == 1:
                action['views'] = [(
                    self.env.ref('product.product_supplierinfo_form_view').id,
                    'form')]
                action['res_id'] = pricelist.ids[0]
            else:
                action['domain'] = [('id', 'in', pricelist.ids)]
            return action
