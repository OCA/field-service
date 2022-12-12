# Copyright 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io

from odoo import api, fields, models


class FsmEquimentQr(models.Model):

    _inherit = "fsm.equipment"

    qrcode = fields.Binary(
        attachment=False,
        store=True,
        readonly=True,
        compute="_compute_qrcode",
    )

    @api.depends("lot_id", "product_id", "url")
    def _compute_qrcode(self):
        for equipment in self:
            equipment_qrcode = self._generate_qrcode_from_url(equipment.url)
            equipment.qrcode = equipment_qrcode

    def _generate_qrcode_from_url(self, url):
        data = io.BytesIO()
        import qrcode

        qrcode.make(url, box_size=4).save(data, optimise=True, format="PNG")
        return base64.b64encode(data.getvalue()).decode()
