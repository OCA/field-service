# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.fieldservice_equipment_portal.controllers.main import PortalEquipment

MAX_ORDER_HISTORY = 50


class PortalEquipmentOrderHistory(PortalEquipment):
    def _equipment_order_history_domain(self, equipment):
        domain = [
            ("equipment_ids", "in", equipment.id),
            ("company_id", "=", equipment.company_id.id),
        ]
        # fieldservice_portal decides which stages portal users may see
        if "portal_visible" in request.env["fsm.stage"]._fields:
            domain.append(("stage_id.portal_visible", "=", True))
        return domain

    def _equipment_get_page_view_values(self, equipment, access_token, **kwargs):
        values = super()._equipment_get_page_view_values(
            equipment, access_token, **kwargs
        )
        # Orders are read with the visitor's own rights: the equipment access
        # check (token or record rule) does not grant access to its orders.
        order_model = request.env["fsm.order"]
        orders = order_model.browse()
        if order_model.has_access("read"):
            orders = order_model.search(
                self._equipment_order_history_domain(equipment),
                order="create_date desc",
                limit=MAX_ORDER_HISTORY,
            )
        values["equipment_orders"] = orders
        return values
