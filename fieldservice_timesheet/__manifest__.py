# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Timesheet",
    "summary": "Timesheet on Field Service Orders",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Project",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        # odoo
        "hr_timesheet",
        # oca/field-service
        "fieldservice_project",
    ],
    "data": [
        "views/fsm_order.xml",
        "views/hr_timesheet.xml",
        "report/report_timesheet_templates.xml",
    ],
    "installable": True,
}
