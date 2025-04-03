# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrderReportTemplate(models.Model):
    _name = "fsm.order.report.template"
    _description = "Field Service Order Report Template"
    _inherit = "fsm.order.report.mixin"

    name = fields.Char(required=True)
