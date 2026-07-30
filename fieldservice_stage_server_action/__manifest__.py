# Copyright (C) 2019, Gray Matter Logic
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Field Service - Stage Server Action",
    "summary": "Execute server actions when reaching a Field Service stage",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "base_automation"],
    "data": [
        "data/ir_server_action.xml",
        "data/fsm_stage.xml",
        "data/base_automation.xml",
        "views/fsm_stage.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
