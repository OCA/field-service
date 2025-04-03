# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Order Report",
    "version": "17.0.1.0.0",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fieldservice_vehicle", "fieldservice_route"],
    "data": [
        "security/ir.model.access.csv",
        "views/report_fsm_order.xml",
        "report/fsm_order_report.xml",
        "wizards/fsm_order_report_wizard.xml",
        "views/fsm_order_report_template.xml",
    ],
}
