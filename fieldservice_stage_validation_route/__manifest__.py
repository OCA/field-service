# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "FSM Stage Validation Route",
    "summary": "Bridge module between fieldservice_stage_validation and fieldservice_route",
    "version": "16.0.1.0.0",
    "category": "Field Service",
    "author": "PyTech-SRL, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_stage_validation",
        "fieldservice_route",
    ],
    "data": [],
    "license": "AGPL-3",
    "development_status": "Beta",
    "auto_install": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
