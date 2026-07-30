# Copyright (C) 2018 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Agreements",
    "summary": "Manage Field Service agreements and contracts",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "depends": ["fieldservice", "agreement"],
    "data": [
        "views/fsm_order_view.xml",
        "views/fsm_equipment_view.xml",
        "views/agreement_view.xml",
        "views/fsm_person.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": [
        "max3903",
        "patrickrwilson",
    ],
}
