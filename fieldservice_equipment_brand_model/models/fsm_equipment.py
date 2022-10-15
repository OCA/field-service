# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    brand_id = fields.Many2one("fsm.equipment.brand")
    model_brand_id = fields.Many2one(
        "fsm.equipment.model", domain="[('brand_id', '=', brand_id)]"
    )

    def _is_valid_equipment_model(self):
        return (
            not self.model_brand_id.brand_id
            or self.model_brand_id.brand_id == self.brand_id
        )

    @api.onchange("brand_id")
    def _onchange_brand_model_id(self):
        for record in self:
            if not record._is_valid_equipment_model():
                record.model_brand_id = False

    @api.constrains("brand_id", "model_brand_id")
    def _constrains_brand_model_id(self):
        for record in self:
            if not record._is_valid_equipment_model():
                raise ValidationError(
                    _("The brand of the model and equipment brand are not the same.")
                )
