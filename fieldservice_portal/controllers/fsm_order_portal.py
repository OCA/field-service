from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "fsm_order_count" in counters:
            fsm_order_count = (
                request.env["fsm.order"].search_count(self._prepare_fsm_orders_domain())
                if request.env["fsm.order"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["fsm_order_count"] = fsm_order_count
        return values

    def _prepare_fsm_orders_domain(self):
        return [("stage_id.portal_visible", "=", True)]

    def _fsm_order_check_access(self, order_id):
        fsm_order = request.env["fsm.order"].browse([order_id])

        try:
            fsm_order.check_access_rights("read")
            fsm_order.check_access_rule("read")
        except AccessError:
            raise
        return fsm_order.sudo()

    def fsm_order_get_page_view_values(self, fsm_order, **kwargs):
        values = {
            "page_name": "fsm_order",
            "fsm_order": fsm_order,
        }

        if kwargs.get("error"):
            values["error"] = kwargs["error"]
        if kwargs.get("warning"):
            values["warning"] = kwargs["warning"]
        if kwargs.get("success"):
            values["success"] = kwargs["success"]

        return values

    @http.route(
        ["/my/fsm_orders", "/my/fsm_orders/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_fsm_orders(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        groupby=None,
        search=None,
        search_in="all",
        **kw,
    ):
        values = self._prepare_portal_layout_values()
        FsmOrder = request.env["fsm.order"]
        domain = self._prepare_fsm_orders_domain()

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "request_early desc"},
            "name": {"label": _("Name"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
            "location": {"label": _("Location"), "order": "location_id"},
            "type": {"label": _("Type"), "order": "type"},
        }

        searchbar_groupby = {
            "none": {"input": "none", "label": _("None")},
            "location_id": {"input": "location", "label": _("Location")},
            "ticket_id": {"input": "ticket", "label": _("Ticket")},
            "stage_id": {"input": "stage", "label": _("Stage")},
            "type": {"input": "type", "label": _("Type")},
        }

        # search input (text)
        searchbar_inputs = OrderedDict(
            (
                ("all", {"input": "all", "label": _("Search in All")}),
                ("name", {"input": "name", "label": _("Search in WO Number")}),
                (
                    "description",
                    {
                        "input": "description",
                        "label": _("Search in Description"),
                    },
                ),
                (
                    "location_id.name",
                    {
                        "input": "location",
                        "label": _("Search in Location Numbers"),
                    },
                ),
            )
        )

        if search and search_in:
            search_domain = []
            for search_property in [
                k
                for (k, v) in searchbar_inputs.items()
                if search_in in (v["input"], "all") and k != "all"
            ]:
                search_domain = OR(
                    [search_domain, [(search_property, "ilike", search)]]
                )
            domain += search_domain

        # search filters (by stage)
        searchbar_filters = OrderedDict(
            (
                str(stage.name),
                {
                    "label": stage.name,
                    "domain": [("stage_id", "=", stage.id)],
                },
            )
            for stage in request.env["fsm.stage"].search(
                [
                    ("stage_type", "=", "order"),
                    ("portal_visible", "=", True),
                ]
            )
        )
        searchbar_filters.update(
            {
                "all": {"label": _("All"), "domain": []},
                "open": {"label": _("Open"), "domain": [("is_closed", "=", False)]},
            }
        )

        # default group by value
        if not groupby:
            groupby = "location_id"
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        # default filter by value
        if not filterby:
            filterby = "open"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        fsm_order_count = FsmOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/fsm_orders",
            url_args={},
            total=fsm_order_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        fsm_orders = FsmOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )

        if groupby == "none":
            grouped_orders = [fsm_orders] if fsm_orders else []
        else:
            grouped_orders = [
                FsmOrder.concat(*g)
                for k, g in groupbyelem(fsm_orders, itemgetter(groupby))
            ]

        values.update(
            {
                "date": date_begin,
                "grouped_orders": grouped_orders,
                "page_name": "fsm_order",
                "pager": pager,
                "default_url": "/my/fsm_orders",
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": searchbar_groupby,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "sortby": sortby,
                "groupby": groupby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("fieldservice_portal.portal_my_fsm_orders", values)

    @http.route(
        ["/my/fsm_order/<int:order_id>"],
        type="http",
        website=True,
    )
    def portal_my_fsm_order(self, order_id=None, **kw):
        try:
            order_sudo = self._fsm_order_check_access(order_id)
        except AccessError:
            return request.redirect("/my")
        values = self.fsm_order_get_page_view_values(order_sudo, **kw)
        return request.render(
            "fieldservice_portal.portal_fieldservice_order_page", values
        )
