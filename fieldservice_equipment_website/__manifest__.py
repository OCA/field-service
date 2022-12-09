# Copyright (C) 2022 Rafnix Guzman rafnixg
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Equipment Website",
    "summary": "Show a website for the equipements",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Odoo Community Association (OCA), Rafnixg",
    "depends": [
        "base",
        "portal",
        "website",
    ],
    "data": [
        "views/fieldservice_equipment_website_templates.xml",
        "views/fieldservice_equipment_views_inherit.xml",
    ],
    "demo": [],
}
