# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLogTags(models.Model):
    _name = "change.log.tag"
    _order = "name"
    _description = "Change Log Tags"

    name = fields.Char(required=True)
    description = fields.Text()
    color = fields.Integer(string="Color Index")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]
