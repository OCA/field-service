# Copyright (C) 2022 - TODAY, Rafnix Guzmán
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    url = fields.Char(store=True, readonly=True, compute="_compute_url")

    def _compute_access_url(self):
        for record in self:
            record.access_url = f"/my/equipments/{record.id}"

    @api.depends("product_id", "lot_id")
    def _compute_url(self):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        for equipment in self:
            serial = equipment.lot_id.name
            url = f"{base_url}/equipment/{serial}"
            equipment.url = url

    def to_controller_url(self):
        if self.url:
            return {
                "type": "ir.actions.act_url",
                "url": self.url,
                "target": "new",
            }
