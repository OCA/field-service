# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Equipment Portal QR Code Labels",
    "summary": "Print QR code labels linking equipments to their portal page",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["fieldservice_equipment_portal", "fieldservice_equipment_stock"],
    "external_dependencies": {"python": ["qrcode"]},
    "data": [
        "views/res_company_views.xml",
        "reports/equipment_label_report.xml",
        "reports/equipment_label_templates.xml",
    ],
}
