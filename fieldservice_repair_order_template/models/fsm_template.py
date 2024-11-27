# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTemplate(models.Model):
    _inherit = "fsm.template"

    repair_order_template_id = fields.Many2one(
        comodel_name="repair.order.template",
        string="Repair Order Template",
        help="If set, this template will be used to create the repair order.",
    )
    type_internal = fields.Selection(related="type_id.internal_type")
