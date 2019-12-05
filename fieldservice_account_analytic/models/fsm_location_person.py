# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocationPerson(models.Model):
    _inherit = 'fsm.location.person'

    customer_id = fields.Many2one('res.partner', string='Billed Customer',
                                  required=True, ondelete='restrict',
                                  auto_join=True,
                                  track_visibility='onchange')
