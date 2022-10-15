# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    type_id = fields.Many2one("fsm.equipment.type")
