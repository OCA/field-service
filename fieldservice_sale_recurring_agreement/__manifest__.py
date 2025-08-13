# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Field Service Recurring Agreement",
    "summary": "Field Service Recurring Agreement",
    "category": "Field Service",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        # OCA/agreement
        "agreement_sale",
        # OCA/field-service
        "fieldservice_agreement",
        "fieldservice_sale_recurring",
    ],
    "website": "https://github.com/OCA/field-service",
    "data": [
        "views/fsm_recurring.xml",
    ],
    "installable": True,
    "maintainer": "imlopes",
}
