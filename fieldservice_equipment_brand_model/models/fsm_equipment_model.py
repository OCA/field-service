# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipmentModel(models.Model):
    _name = "fsm.equipment.model"
    _description = "FSM Equipment Model"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    brand_id = fields.Many2one("fsm.equipment.brand", required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
