# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.website_sale_checkout_address_restrict.controllers import (
    main as website_sale_controller,
)


class WebsiteSale(website_sale_controller.WebsiteSale):
    def checkout_values(self, **kw):
        values = super().checkout_values(**kw)

        shippings = values["shippings"]
        valid_ids = self._get_valid_fsm_shipping_ids(shippings)
        values["shippings"] = shippings.filtered(lambda p: p.id in valid_ids)

        return values

    def _get_valid_fsm_shipping_ids(self, partners):
        locations = (
            request.env["fsm.location"]
            .sudo()
            .search(
                [
                    ("partner_id", "in", partners.ids),
                    ("fsm_route_id", "!=", False),
                    ("fsm_route_id.fsm_person_id", "!=", False),
                    ("fsm_route_id.day_ids", "!=", False),
                    ("fsm_route_id.max_order", ">", 0),
                ]
            )
        )
        return locations.mapped("partner_id").ids
