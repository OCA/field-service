# Copyright (C) 2019 - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Contracts",
    "summary": "Manage FSM Contracts",
    "author": "Akretion, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "depends": [
        "contract",
        "product_contract",
        "fieldservice_sale",
        "fieldservice_recurring",
        "fieldservice_sale_recurring",
        "fieldservice_sale_frequency",
        "fieldservice_recurring_quick_edit",
    ],
    "data": [
        "views/contract.xml",
        "views/contract_line.xml",
        "views/fsm_recurring.xml",
        "views/fsm_order.xml",
        "views/sale_view.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": [
        "hparfr",
    ],
}
