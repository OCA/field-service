# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Agreements",
    "summary": "Manage Field Service agreements and contracts",
    "author": "Open Source Integrators, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "depends": ["fieldservice", "agreement_serviceprofile"],
    "data": [
        "views/fsm_order_view.xml",
        "views/fsm_equipment_view.xml",
        "views/agreement_view.xml",
        "views/fsm_person.xml",
        "views/fsm_location.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": [
        "max3903",
        "bodedra",
        "smangukiya",
        "osi-scampbell",
        "patrickrwilson",
    ],
}
