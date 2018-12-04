# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    branch_id = fields.Many2one('branch', string='Branch')
    district_id = fields.Many2one('district', string='District')
    region_id = fields.Many2one('region', string='Region')
    
    @api.onchange('fsm_location_id')
    def onchange_fsm_location_id(self):
        if self.fsm_location_id:
            self.branch_id = self.fsm_location_id.branch_id or False
            self.district_id = self.fsm_location_id.district_id or False
            self.region_id = self.fsm_location_id.region_id or False
