# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.fieldservice_equipment_portal.controllers.main import PortalEquipment


class PortalEquipmentCalibration(PortalEquipment):
    @http.route(
        "/my/equipments/calibration/<int:certificate_id>/download",
        type="http",
        auth="public",
        website=True,
    )
    def portal_equipment_calibration_download(
        self, certificate_id, access_token=None, **kw
    ):
        """Certificate download honoring the same access rules as the
        equipment page (portal user / access token / public setting)."""
        certificate = (
            request.env["fsm.calibration.certificate"]
            .sudo()
            .browse(certificate_id)
            .exists()
        )
        if not certificate or not certificate.certificate_file:
            raise request.not_found()
        try:
            self._document_check_access(
                "fsm.equipment", certificate.fsm_equipment_id.id, access_token
            )
        except (AccessError, MissingError):
            if not self._equipment_public_access_enabled():
                return request.redirect("/my")
        return (
            request.env["ir.binary"]
            ._get_stream_from(
                certificate, "certificate_file", filename=f"{certificate.name}.pdf"
            )
            .get_response(as_attachment=True)
        )
