# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.fieldservice_equipment_portal.controllers.main import PortalEquipment

MAX_ORDER_HISTORY = 50


class PortalEquipmentOrderHistory(PortalEquipment):
    def _equipment_get_page_view_values(self, equipment, access_token, **kwargs):
        values = super()._equipment_get_page_view_values(
            equipment, access_token, **kwargs
        )
        # sudo: the visitor already passed the equipment page access check;
        # the order history is part of the equipment's public record.
        values["equipment_orders"] = (
            request.env["fsm.order"]
            .sudo()
            .search(
                [("equipment_ids", "in", equipment.id)],
                order="create_date desc",
                limit=MAX_ORDER_HISTORY,
            )
        )
        return values
