# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskPhone(models.Model):
    _inherit='helpdesk.ticket'

    phone = fields.Char(string="Phone", widget="phone")
