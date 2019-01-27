# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base_geoengine import geo_model


class FSMOrder(geo_model.GeoModel):
    _inherit = 'fsm.order'

    skill_ids = fields.Many2many('hr.skill', string="Required Skills")

    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        if not self.template_id:
            skill_ids = []
            for category in self.category_ids:
                skill_ids.extend([skill.id for skill in category.skill_ids])
            self.skill_ids = [(6, 0, skill_ids)]

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.category_ids = self.template_id.category_ids
            self.skill_ids = self.template_id.skill_ids
            self.todo = self.template_id.instructions
