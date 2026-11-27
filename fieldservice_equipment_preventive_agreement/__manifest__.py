# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Equipment Preventive Maintenance Agreement",
    "summary": "Preventive visits for the equipments of one agreement",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["fieldservice_equipment_preventive", "fieldservice_agreement"],
    "data": [
        "security/ir.model.access.csv",
        "views/agreement_views.xml",
        "views/fsm_recurring_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "auto_install": True,
}
