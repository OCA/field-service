# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    is_a_distribution = fields.Boolean(string='Is a Distribution')
    dist_parent_id = fields.Many2one('fsm.location',
                                     string='Distribution Parent')
