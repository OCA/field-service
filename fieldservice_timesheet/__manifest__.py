# Copyright 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Timesheet",
    "summary": "Timesheet on Field Service Orders",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "category": "Project",
    "website": "https://github.com/OCA/field-service",
    "maintainers": ["max3903"],
    "depends": [
        "hr_timesheet",
        "project",
        "fieldservice",
    ],
    "data": [
        "views/fsm_order.xml",
        "views/hr_timesheet.xml",
        "report/report_timesheet_templates.xml",
    ],
    "installable": True,
    "development_status": "Beta",
}
