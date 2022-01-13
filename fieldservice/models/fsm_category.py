# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMCategory(models.Model):
    _name = "fsm.category"
    _description = "Field Service Worker Category"

    name = fields.Char(required="True")
    parent_id = fields.Many2one("fsm.category", string="Parent")
    color = fields.Integer("Color Index", default=10)
    full_name = fields.Char(compute="_compute_full_name")
    description = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
        help="Company related to this category",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Category name already exists!")]

    def _compute_full_name(self):
        for record in self:
            if record.parent_id:
                record.full_name = record.parent_id.full_name + "/" + record.name
            else:
                record.full_name = record.name
