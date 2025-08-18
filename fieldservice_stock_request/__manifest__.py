# Copyright (C) 2021 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Stock Request",
    "summary": "Integrate Stock Requests with Field Service Orders",
    "version": "17.0.1.1.0",
    "category": "Field Service",
    "author": "Open Source Integrators, "
    "Brian McMaster, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_stock",
        "stock_request_direction",
        "stock_request_picking_type",
        "stock_request_submit",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_order.xml",
        "views/stock.xml",
        "views/stock_request.xml",
        "views/stock_request_order.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["brian10048", "wolfhall", "max3903", "smangukiya"],
}
