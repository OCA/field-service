# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_geoengine import geo_model


class FSMLocation(geo_model.GeoModel):
    _inherit = 'fsm.location'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
