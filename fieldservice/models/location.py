# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Location(models.Model):
    _name = 'location'
    _description = 'Location'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    _rec_name = 'complete_name'

    name = fields.Char(string='Name')
    complete_name = fields.Char("Full Location Name",
                                compute='_compute_complete_name',
                                store=True, index=True)
    parent_id = fields.Many2one('location', string='Parent Location',
                                ondelete='restrict')
    notes = fields.Html(string='Notes')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)

    @api.one
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        if self.parent_id.complete_name:
            self.complete_name = '%s/%s' % \
                                 (self.parent_id.complete_name, self.name)
        else:
            self.complete_name = self.name
