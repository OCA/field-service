# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request


class PortalEquipmentSerial(http.Controller):
    @http.route(
        "/my/equipments/serial/<serial>",
        type="http",
        auth="public",
        website=True,
    )
    def portal_equipment_by_serial(self, serial, **kw):
        """Resolve an equipment by its serial number and redirect to its
        page. Keeps printed QR labels stable even if the equipment id
        changes; access control happens on the target page."""
        equipment = (
            request.env["fsm.equipment"]
            .sudo()
            .search([("lot_id.name", "=ilike", serial)], limit=1)
        )
        if not equipment:
            raise request.not_found()
        return request.redirect(f"/my/equipments/{equipment.id}", code=301)
