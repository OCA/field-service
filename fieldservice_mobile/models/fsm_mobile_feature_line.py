# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FSMMobileFeatureLine(models.Model):
    _name = "fsm.mobile.feature.line"
    _description = "FSM Mobile Feature Line"

    feature_id = fields.Many2one("fsm.mobile.feature.mapping", string="Feature Mapping")
    name = fields.Char(string="Feature Name")
    group_ids = fields.Many2many("res.groups", string="Groups")
    code = fields.Char()
