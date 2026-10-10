# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Purchase Request Equipment",
    "summary": "Open the purchase requests of an equipment from its form",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": [
        "fieldservice_purchase_request",
        "fieldservice_equipment_order_history",
    ],
    "data": ["views/fsm_equipment_views.xml"],
    "auto_install": True,
}
