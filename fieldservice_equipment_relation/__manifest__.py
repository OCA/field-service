# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Equipment Relations",
    "summary": "Manage typed relations between Field Service equipment",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "license": "AGPL-3",
    "depends": ["fieldservice"],
    "data": [
        "security/ir.model.access.csv",
        "data/fsm_equipment_relation_type.xml",
        "views/fsm_equipment_relation_type_views.xml",
        "views/fsm_equipment_relation_views.xml",
        "views/fsm_equipment_views.xml",
        "views/menu.xml",
    ],
    "demo": ["demo/fsm_equipment_relation_demo.xml"],
    "installable": True,
    "development_status": "Beta",
}
