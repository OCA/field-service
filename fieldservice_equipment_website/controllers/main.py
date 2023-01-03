import logging

# import odoo.http as http
from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class FieldserviceEquipmentWebsiteController(http.Controller):
    """Custom route for QRcode scan."""

    @http.route("/equipment/<serial>/", type="http", auth="public", website=True)
    def get_equipment(self, serial):

        Lots = http.request.env["stock.production.lot"]
        lot_obj = Lots.sudo().search([["name", "ilike", serial]], limit=1)
        return (
            http.request.render(
                "fieldservice_equipment_website.index", {"lot_obj": lot_obj}
            )
            if lot_obj
            else http.request.render("website.page_404")
        )


class PortalFieldservice(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "equipment_count" in counters:
            self._set_count_to_values("fsm.equipment", values, "equipment_count")
        if "location_count" in counters:
            partner_id = request.env.user.partner_id.parent_id
            if partner_id.parent_id:
                partner_id = partner_id.parent_id
            self._set_count_to_values("fsm.location", values, "location_count")
        return values

    def _set_count_to_values(self, model_name, values, key, domain=None):
        if domain is None:
            domain = []
        obj_model = request.env[model_name]
        count = (
            obj_model.search_count(domain)
            if obj_model.check_access_rights("read", raise_exception=False)
            else 0
        )
        values[key] = count

    def _fieldservice_equipment_get_page_view_values(
        self, equipment, access_token, **kwargs
    ):
        values = {
            "page_name": "Equipments",
            "equipment": equipment,
        }
        return self._get_page_view_values(
            equipment, access_token, values, "my_equipments_history", False, **kwargs
        )

    def _fieldservice_location_get_page_view_values(
        self, location, access_token, **kwargs
    ):
        values = {
            "page_name": "Locations",
            "location": location,
        }
        return self._get_page_view_values(
            location, access_token, values, "my_locations_history", False, **kwargs
        )

    def _get_filter_domain(self, kw):
        return []

    @http.route(
        ["/my/equipments", "/my/equipments/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_equipments(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        fieldservice_equipment_obj = request.env["fsm.equipment"]
        # Avoid error if the user does not have access.
        if not fieldservice_equipment_obj.check_access_rights(
            "read", raise_exception=False
        ):
            return request.redirect("/my")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            # "date": {"label": _("Date"), "order": "recurring_next_date desc"},
            "name": {"label": _("Name"), "order": "name desc"},
            "code": {"label": _("Reference"), "order": "code desc"},
        }
        # default sort by order
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]
        # count for pager
        equipment_count = fieldservice_equipment_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/equipments",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=equipment_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        equipments = fieldservice_equipment_obj.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_equipments_history"] = equipments.ids[:100]
        values.update(
            {
                "date": date_begin,
                "equipments": equipments,
                "page_name": "Equipments",
                "pager": pager,
                "default_url": "/my/equipments",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render(
            "fieldservice_equipment_website.portal_my_equipments", values
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
        values = self._fieldservice_equipment_get_page_view_values(
            equipment_sudo, access_token, **kw
        )
        return request.render(
            "fieldservice_equipment_website.portal_equipment_page", values
        )

    @http.route(
        ["/my/locations", "/my/locations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_locations(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        fieldservice_location_obj = request.env["fsm.location"].sudo()
        # Avoid error if the user does not have access.
        if not fieldservice_location_obj.check_access_rights(
            "read", raise_exception=False
        ):
            return request.redirect("/my")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            # "date": {"label": _("Date"), "order": "recurring_next_date desc"},
            "name": {"label": _("Name"), "order": "name desc"},
            "code": {"label": _("Reference"), "order": "code desc"},
        }
        # default sort by order
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]
        # count for pager
        location_count = fieldservice_location_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/locations",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=location_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        locations = fieldservice_location_obj.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_locations_history"] = locations.ids[:100]
        values.update(
            {
                "date": date_begin,
                "locations": locations,
                "page_name": "Locations",
                "pager": pager,
                "default_url": "/my/locations",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render(
            "fieldservice_equipment_website.portal_my_locations", values
        )

    @http.route(
        ["/my/locations/<int:location_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_location_detail(self, location_id, access_token=None, **kw):
        try:
            location_sudo = self._document_check_access(
                "fsm.location", location_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._fieldservice_location_get_page_view_values(
            location_sudo, access_token, **kw
        )
        return request.render(
            "fieldservice_equipment_website.portal_location_page", values
        )
