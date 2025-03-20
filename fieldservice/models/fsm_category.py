# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMCategory(models.Model):
    _name = "fsm.category"
    _description = "Field Service Worker Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "full_name"
    _order = "full_name"

    name = fields.Char(required=True)
    full_name = fields.Char(compute="_compute_full_name", store=True, recursive=True)
    parent_id = fields.Many2one("fsm.category", string="Parent", index=True)
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many("fsm.category", "parent_id", "Child Categories")
    color = fields.Integer("Color Index", default=10)
    description = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=False,
        index=True,
        help="Company related to this category",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Category name already exists!")]

    @api.depends("name", "parent_id.full_name")
    def _compute_full_name(self):
        for record in self:
            record.full_name = (
                record.parent_id.full_name + " / " + record.name
                if record.parent_id
                else record.name
            )
