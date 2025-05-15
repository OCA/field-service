# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Stock Route",
    "version": "15.0.1.0.3",
    "summary": "Link between Field Service Sale Stock and Route",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_sale_stock",
        "fieldservice_route",
    ],
    "data": ["views/fsm_order.xml", "views/sale_order.xml", "views/fsm_route.xml"],
}
