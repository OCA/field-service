# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalEquipment(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "equipment_count" in counters:
            equipment_model = request.env["fsm.equipment"]
            equipment_count = (
                equipment_model.search_count([])
                if equipment_model.has_access("read")
                else 0
            )
            values["equipment_count"] = equipment_count
        return values

    def _equipment_get_page_view_values(self, equipment, access_token, **kwargs):
        values = {
            "page_name": "Equipments",
            "equipment": equipment,
        }
        return self._get_page_view_values(
            equipment, access_token, values, "my_equipments_history", False, **kwargs
        )

    def _get_filter_domain(self, kw):
        return []

    @http.route(
        ["/my/equipments", "/my/equipments/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_equipments(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        equipment_model = request.env["fsm.equipment"]
        if not equipment_model.has_access("read"):
            return request.redirect("/my")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name desc"},
        }
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]
        equipment_count = equipment_model.search_count(domain)
        pager = portal_pager(
            url="/my/equipments",
            url_args={"sortby": sortby},
            total=equipment_count,
            page=page,
            step=self._items_per_page,
        )
        equipments = equipment_model.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_equipments_history"] = equipments.ids[:100]
        values.update(
            {
                "equipments": equipments,
                "page_name": "Equipments",
                "pager": pager,
                "default_url": "/my/equipments",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render(
            "fieldservice_equipment_portal.portal_my_equipments", values
        )

    @http.route(
        ["/my/equipments/<int:equipment_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_equipment_detail(self, equipment_id, access_token=None, **kw):
        try:
            equipment_sudo = self._document_check_access(
                "fsm.equipment", equipment_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._equipment_get_page_view_values(
            equipment_sudo, access_token, **kw
        )
        return request.render(
            "fieldservice_equipment_portal.portal_equipment_page", values
        )
