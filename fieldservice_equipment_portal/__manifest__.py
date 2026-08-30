# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Equipment Portal",
    "summary": "Let portal users see their field service equipments",
    "version": "18.0.1.2.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["portal", "fieldservice"],
    "data": [
        "security/ir.model.access.csv",
        "security/fsm_equipment_security.xml",
        "views/portal_templates.xml",
        "views/res_config_settings.xml",
    ],
}
