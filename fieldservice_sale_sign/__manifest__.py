# Copyright (C) 2025 APSL-Nagarro Bernat Obrador bobrador@apsl.net
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Sales Sign",
    "version": "15.0.1.0.0",
    "summary": "Sign Field Service Sales Orders",
    "category": "Field Service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_order.xml",
        "wizard/fsm_order_signature_wizard.xml",
    ],
    "license": "AGPL-3",
    "maintainers": ["BernatObrador"],
    "installable": True,
}
