# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    rel_count = fields.Integer(string='Relations',
                               compute='_compute_relation_count')

    @api.multi
    def _compute_relation_count(self):
        for location in self:
            location.rel_count = self.env['res.partner.relation.all'].\
                search_count([('this_partner_id', '=', location.name)])

    @api.multi
    def action_view_relations(self):
        """
        This function returns an action that display existing
        partner relations of a given fsm location id.
        """
        for location in self:
            action = self.env.\
                ref('partner_multi_relation.tree_res_partner_relation_all').\
                read()[0]
            relations = self.env['res.partner.relation.all'].\
                search([('this_partner_id', '=', location.name)])
            action = self.env.\
                ref('partner_multi_relation.action_res_partner_relation_all')\
                .read()[0]
            action['domain'] = [('id', 'in', relations.ids)]
            return action
