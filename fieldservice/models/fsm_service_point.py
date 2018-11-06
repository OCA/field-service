# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMServicePoint(models.Model):
    _name = 'fsm.service.point'
    _description = 'Service Point'
    _order = 'fsm_service_point_type asc, sequence asc'

    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char("Complete Name",
                                compute='_compute_complete_name',
                                store=True, index=True)
    sequence = fields.Integer('Sequence', index=True, default=1)
    fsm_location_id = fields.Many2one('fsm.location', string="Location",
                                      index=True)
    fsm_service_point_type = fields.Many2one('fsm.service.point.type',
                                             string='Type', required=True)
    parent_id = fields.Many2one('fsm.service.point', 
                                string='Parent Service Point', 
                                ondelete='restrict')
    child_ids = fields.One2many('fsm.service.point', 'parent_id',
                                    'Child Service Points')
    notes = fields.Html(string='Notes')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for p in self:
            if p.parent_id:
                p.complete_name = '%s / %s' % \
                                  (p.parent_id.complete_name, p.name)
            else:
                p.complete_name = p.name


class FSMServicePointType(models.Model):
    _name = 'fsm.service.point.type'
    _description = 'Service Point Type'
    _order = 'name asc'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char("Complete Name",
                                compute='_compute_complete_name',
                                store=True, index=True)
    parent_id = fields.Many2one('fsm.service.point.type', 'Parent Type',
                                index=True, ondelete='cascade')
    child_ids = fields.One2many('fsm.service.point.type', 'parent_id',
                                'Child Types')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for type in self:
            if type.parent_id:
                type.complete_name = '%s / %s' % \
                                     (type.parent_id.complete_name, type.name)
            else:
                type.complete_name = type.name

    @api.constrains('parent_id')
    def _check_type_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create a recursive type.'))
