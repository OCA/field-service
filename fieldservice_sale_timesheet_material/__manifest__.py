# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Timesheet & Material",
    "summary": "Invoice field service timesheets and consumed materials "
    "by adding them to the sale order",
    "version": "16.0.1.0.0",
    "category": "Field Service",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_sale",
        "fieldservice_account_analytic",
        "fieldservice_stock",
    ],
    "data": [
        "views/fsm_order.xml",
        "report/fsm_order_report_template.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "installable": True,
}
