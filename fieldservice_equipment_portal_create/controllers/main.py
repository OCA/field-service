# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.http import request


class PortalEquipmentCreate(http.Controller):
    """Portal registration of locations and equipments.

    Every posted id is resolved as the portal user, through ACLs and record
    rules scoped to the commercial partner, and every check runs before the
    first write. Creations then run with sudo over WHITELISTED values with
    ownership forced to the user's commercial partner (fsm.location
    delegation-inherits res.partner, which portal users cannot create);
    direct RPC creation stays blocked. The serial number is typed and the
    lot is found or created under the selected product, in the company of
    the equipment, so equipment, product and serial can never diverge.
    """

    # products offered at once on the registration form; narrow with search
    _products_limit = 80

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
        name = (kw.get("name") or "").strip()
        if not name:
            return request.render(
                "fieldservice_equipment_portal_create.portal_create_location",
                {"error": _("The location name is required."), "values": kw},
            )
        partner = self._commercial_partner()
        # read as the portal user: the record rule limits it to the partner
        parent = request.env["fsm.location"].search(
            [("owner_id", "=", partner.id), ("parent_id", "=", False)],
            order="id",
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
                    "name": name,
                    "parent_id": parent.id,
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

    def _equipment_form_values(self, search=None):
        partner = self._commercial_partner()
        locations = request.env["fsm.location"].search(
            [("owner_id", "child_of", partner.id)]
        )
        domain = self._get_registrable_products_domain()
        if search:
            domain += [
                "|",
                ("name", "ilike", search),
                ("default_code", "ilike", search),
            ]
        products = request.env["product.product"].search(
            domain, limit=self._products_limit + 1
        )
        return {
            "locations": locations,
            "products": products[: self._products_limit],
            "products_truncated": len(products) > self._products_limit,
            "search": search or "",
        }

    def _render_equipment_form(self, error=None, values=None, search=None):
        form_values = self._equipment_form_values(search=search)
        form_values.update({"error": error, "values": values or {}})
        return request.render(
            "fieldservice_equipment_portal_create.portal_create_equipment",
            form_values,
        )

    @http.route("/my/equipments/new", type="http", auth="user", website=True)
    def portal_new_equipment(self, search=None, **kw):
        return self._render_equipment_form(search=(search or "").strip())

    def _to_id(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _check_equipment_values(self, kw):
        """Resolve and check the posted values as the portal user.

        Return ``(error, values)``: an error message to show on the form, or
        the values to create the equipment and to find or create its lot.
        """
        location = request.env["fsm.location"].search(
            [
                ("id", "=", self._to_id(kw.get("location_id"))),
                ("owner_id", "child_of", self._commercial_partner().id),
            ]
        )
        if not location:
            return _("Select one of your locations."), None
        product = request.env["product.product"].search(
            [("id", "=", self._to_id(kw.get("product_id")))]
            + self._get_registrable_products_domain()
        )
        if not product:
            return _("Select one of the products offered."), None
        name = (kw.get("name") or "").strip()
        serial = (kw.get("serial") or "").strip()
        if not name or not serial:
            return _("The name and the serial number are required."), None
        equipment_name = f"{name} - {serial}"
        equipment_model = request.env["fsm.equipment"].sudo()
        if equipment_model.search_count([("name", "=", equipment_name)], limit=1):
            return _("An equipment named %s already exists.", equipment_name), None
        company = location.sudo().company_id or request.env.user.company_id
        lot = (
            request.env["stock.lot"]
            .sudo()
            .search(
                [
                    ("name", "=", serial),
                    ("product_id", "=", product.id),
                    ("company_id", "in", [company.id, False]),
                ],
                limit=1,
            )
        )
        if lot.fsm_equipment_id:
            return (
                _("The serial number %s is already registered.", serial),
                None,
            )
        return None, {
            "name": equipment_name,
            "location": location,
            "product": product,
            "serial": serial,
            "company": company,
            "lot": lot,
        }

    @http.route(
        "/my/equipments/submit",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def portal_submit_equipment(self, **kw):
        error, values = self._check_equipment_values(kw)
        if error:
            return self._render_equipment_form(error=error, values=kw)
        partner = self._commercial_partner()
        # find-or-create the serial under the selected product: keeps
        # equipment, product and lot always consistent. Lot creation is the
        # single narrowly-sudo'ed write (portal users are not stock users).
        lot = values["lot"] or (
            request.env["stock.lot"]
            .sudo()
            .create(
                {
                    "name": values["serial"],
                    "product_id": values["product"].id,
                    "company_id": values["company"].id,
                }
            )
        )
        # same rationale as the location: controlled sudo, forced ownership
        equipment = (
            request.env["fsm.equipment"]
            .sudo()
            .create(
                {
                    "name": values["name"],
                    "location_id": values["location"].id,
                    "owned_by_id": partner.id,
                    "managed_by_id": partner.id,
                    "product_id": values["product"].id,
                    "lot_id": lot.id,
                    "company_id": values["company"].id,
                }
            )
        )
        equipment.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        return request.redirect(f"/my/equipments/{equipment.id}")
