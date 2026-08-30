# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io

import qrcode

from odoo import api, fields, models


class FsmEquipment(models.Model):
    _inherit = "fsm.equipment"

    qrcode = fields.Binary(
        compute="_compute_qrcode",
        attachment=False,
        readonly=True,
        help="QR code pointing to this equipment's portal page.",
    )

    def _get_qrcode_url(self):
        self.ensure_one()
        return f"{self.get_base_url()}{self.access_url}"

    @api.depends("lot_id", "product_id")
    def _compute_qrcode(self):
        for equipment in self:
            if not equipment.id:
                equipment.qrcode = False
                continue
            equipment.qrcode = equipment._generate_qrcode_from_url(
                equipment._get_qrcode_url()
            )

    @api.model
    def _generate_qrcode_from_url(self, url):
        data = io.BytesIO()
        qrcode.make(url, box_size=8, border=0).save(data, format="PNG")
        return base64.b64encode(data.getvalue()).decode()
