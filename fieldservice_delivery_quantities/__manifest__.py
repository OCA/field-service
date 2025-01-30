# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Delivery Quantities",
    "version": "15.0.1.0.0",
    "summary": "This module provides an easy way to review the quantities to be ",
    "delivered on a given day." "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fieldservice_sale_stock", "fieldservice_route"],
    "data": ["security/ir_rule.xml", "views/stock_move_views.xml", "views/menu.xml"],
}
