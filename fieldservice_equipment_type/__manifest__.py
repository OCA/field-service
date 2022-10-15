# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Equipment Type",
    "summary": "Field Service Equipment Type",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Field Service",
    "depends": ["fieldservice"],
    "website": "https://github.com/OCA/field-service",
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_equipment_type.xml",
        "views/fsm_equipment.xml",
    ],
    "installable": True,
}
