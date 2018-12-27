# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Equipment Agreement",
    "summary": "Manage FSM Equipment Agreements",
    "author": "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "11.0.1.0.0",
    "depends": [
        "fieldservice",
        "agreement",
    ],
    "data": [
        "views/agreement_view.xml",
        "views/fsm_equipment_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": [
        "max3903",
        "smangukiya",
    ],
}
