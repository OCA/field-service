# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Field Service Equipment Warranty",
    "summary": "Field Service equipment warranty",
    "category": "Field Service",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        # OCA/RMA
        "product_warranty",
        # OCA/field-service
        "fieldservice_equipment_stock",
    ],
    "website": "https://github.com/OCA/field-service",
    "data": [
        # Views
        "views/fsm_equipment.xml",
    ],
    "installable": True,
    "maintainers": ["imlopes"],
}
