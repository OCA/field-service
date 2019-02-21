# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.base_geoengine import geo_model


class FSMLocation(geo_model.GeoModel):
    _inherit = 'fsm.location'

    is_a_distribution = fields.Boolean(string='Is a Distribution')
    dist_parent_id = fields.Many2one('fsm.location',
                                     string='Distribution Parent')

    distrib_count = fields.Integer(
        compute='_compute_distrib_sublocation_ids',
        string='# of distributed sub-locations')

    @api.multi
    def _compute_distrib_sublocation_ids(self):
        for location in self:
            for child in location:
                child_locs = self.env['fsm.location'].search(
                    [('fsm_parent_id', '=', child.id)])
                count = self.env['fsm.location'].search_count(
                    [('fsm_parent_id', '=', child.id),
                     ('is_a_distribution', '=', True)])
            if child_locs:
                for loc in child_locs:
                    count += loc.distrib_count
            location.distrib_count = count

    @api.multi
    def action_view_distrib_sublocation(self):
        '''
        This function returns an action that display existing
        distribution sub-locations of a given fsm location id.
        It can either be a in a list or in a form view, if there is only one
        sub-location to show.
        '''
        for location in self:
            action = self.env.ref('fieldservice.action_fsm_location').read()[0]
            sublocation = self.get_action_views(0, 0, location)
            sublocation.filtered(lambda r: r.is_a_distribution)
            if len(sublocation) > 1 or len(sublocation) == 0:
                action['domain'] = [('id', 'in', sublocation.ids),
                                    ('is_a_distribution', '=', True)]
            elif sublocation:
                action['views'] = [(self.env.
                                    ref('fieldservice.' +
                                        'fsm_location_form_view').id,
                                    'form')]
                action['res_id'] = sublocation.id
            return action
