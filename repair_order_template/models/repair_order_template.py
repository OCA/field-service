# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RepairOrderTemplate(models.Model):
    _name = "repair.order.template"
    _description = "Repair Order Template"
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    tag_ids = fields.Many2many("repair.tags", string="Tags")
    internal_notes = fields.Html()
    under_warranty = fields.Boolean()
    product_id = fields.Many2one(
        "product.product",
        string="Product to Repair",
        domain=[("type", "=", "consu")],
        check_company=True,
    )
    line_ids = fields.One2many(
        comodel_name="repair.order.template.line",
        inverse_name="template_id",
        check_company=True,
    )
