# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request


class PortalEquipmentCreate(http.Controller):
    """Portal registration of locations and equipments.

    Reads run as the portal user through ACLs and record rules scoped to
    the commercial partner. Creations run with sudo over WHITELISTED values
    with ownership forced to the user's commercial partner (fsm.location
    delegation-inherits res.partner, which portal users cannot create);
    direct RPC creation stays blocked. The serial number is typed and the
    lot is found or created under the selected product, so equipment,
    product and serial can never diverge.
    """

    def _commercial_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    @http.route("/my/locations/new", type="http", auth="user", website=True)
    def portal_new_location(self, **kw):
        return request.render(
            "fieldservice_equipment_portal_create.portal_create_location", {}
        )

    @http.route(
        "/my/locations/submit",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_submit_location(self, **kw):
        partner = self._commercial_partner()
        parent = request.env["fsm.location"].search(
            [("partner_id", "=", partner.id), ("fsm_parent_id", "=", False)],
            limit=1,
        )
        # sudo with whitelisted values + forced ownership: fsm.location
        # delegation-inherits res.partner, which portal users cannot create.
        # Direct RPC create stays blocked (no create ACL for portal).
        location = (
            request.env["fsm.location"]
            .sudo()
            .create(
                {
                    "name": kw.get("name"),
                    "fsm_parent_id": parent.id if parent else False,
                    "owner_id": partner.id,
                    "phone": kw.get("phone"),
                    "email": kw.get("email"),
                    "street": kw.get("street"),
                    "city": kw.get("city"),
                    "zip": kw.get("zip"),
                }
            )
        )
        location.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        return request.redirect("/my/equipments/new")

    def _get_registrable_products_domain(self):
        """Products a portal user may register equipments for.

        Extend to narrow the catalog (e.g. maintainable products only).
        """
        return [("tracking", "!=", "none"), ("is_storable", "=", True)]

    @http.route("/my/equipments/new", type="http", auth="user", website=True)
    def portal_new_equipment(self, **kw):
        partner = self._commercial_partner()
        locations = request.env["fsm.location"].search(
            [("owner_id", "child_of", partner.id)]
        )
        products = request.env["product.product"].search(
            self._get_registrable_products_domain()
        )
        return request.render(
            "fieldservice_equipment_portal_create.portal_create_equipment",
            {"locations": locations, "products": products},
        )

    @http.route(
        "/my/equipments/submit",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_submit_equipment(self, **kw):
        partner = self._commercial_partner()
        product = request.env["product.product"].browse(int(kw.get("product_id")))
        serial = (kw.get("serial") or "").strip()
        # find-or-create the serial under the selected product: keeps
        # equipment, product and lot always consistent. Lot creation is the
        # single narrowly-sudo'ed write (portal users are not stock users).
        lot = (
            request.env["stock.lot"]
            .sudo()
            .search([("name", "=", serial), ("product_id", "=", product.id)], limit=1)
        )
        if not lot:
            lot = (
                request.env["stock.lot"]
                .sudo()
                .create({"name": serial, "product_id": product.id})
            )
        # same rationale as the location: controlled sudo, forced ownership
        equipment = (
            request.env["fsm.equipment"]
            .sudo()
            .create(
                {
                    "name": f"{kw.get('name')} - {serial}",
                    "location_id": int(kw.get("location_id")),
                    "owned_by_id": partner.id,
                    "managed_by_id": partner.id,
                    "product_id": product.id,
                    "lot_id": lot.id,
                }
            )
        )
        equipment.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        return request.redirect(f"/my/equipments/{equipment.id}")
