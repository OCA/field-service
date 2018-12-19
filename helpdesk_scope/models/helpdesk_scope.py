# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskScope(models.Model):
    _name='helpdesk.scope'

    helpdesk_scope = fields.Char(string="Scope")
    description = fields.Text(string="Description")
