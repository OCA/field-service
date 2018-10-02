# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fsm_location = fields.Boolean('Is a FS Location')
    fsm_person = fields.Boolean('Is a FS Person')
