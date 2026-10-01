# Copyright (C) 2026 Innovyou - Lorenzo Carta <https://www.innovyou.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Recurring Timesheet & Material",
    "summary": "Add the timesheets and materials of the field service orders "
    "of a recurring order to the sale order that sold it",
    "version": "16.0.1.0.0",
    "category": "Field Service",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_sale_recurring",
        "fieldservice_sale_timesheet_material",
    ],
    "data": [
        "views/fsm_order.xml",
        "views/fsm_recurring.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
}
