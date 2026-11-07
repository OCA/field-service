# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Stock Route Backorder",
    "version": "18.0.1.0.0",
    "summary": "Manage backorders for Field Service Orders",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fieldservice_sale_stock_route"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/fsm_partial_delivery_wizard_form.xml",
        "views/fsm_order_view.xml",
        "views/product_template.xml",
    ],
}
