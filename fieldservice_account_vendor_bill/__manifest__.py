# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Field service Vendor Bill",
    "summary": "Accounting field services customizations",
    "category": "Field Service",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        # Odoo/core
        "account",
        # OCA/field-service
        "fieldservice",
    ],
    "website": "https://github.com/OCA/field-service",
    "data": [
        "views/fsm_order.xml",
    ],
    "installable": True,
    "maintainer": "ivantodorovich",
}
