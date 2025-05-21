# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Website Sale Checkout Address Filter",
    "version": "15.0.1.0.0",
    "summary": "Filter FSM locations in website sale checkout",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_sale_stock_route",
        "website_sale_checkout_address_restrict",
    ],
    "data": ["views/website_sale_templates.xml"],
}
