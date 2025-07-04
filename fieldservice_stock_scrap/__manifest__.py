# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Stock Scrap",
    "summary": "Scrap stock from Field Service order of Stock Requests",
    "version": "17.0.1.2.0",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "Antoni Marroig, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_stock_request",
    ],
    "data": [
        "views/fsm_order.xml",
        "views/stock_scrap.xml",
        "security/ir.model.access.csv",
        "wizards/scrap_stock_wizard.xml",
        "data/stock_location.xml",
    ],
}
