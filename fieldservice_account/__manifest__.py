# Copyright (C) 2018 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Accounting",
    "summary": "Track invoices linked to Field Service orders",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/fsm_order.xml",
        "views/fsm_stage.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["osimallen", "brian10048"],
    "installable": True,
}
