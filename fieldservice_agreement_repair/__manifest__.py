# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Agreement Repair",
    "summary": "Fieldservice Agreement Repair",
    "category": "Field Service",
    "version": "17.0.1.0.0",
    "author": "Camptocamp SA, Italo Lopes, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainer": "Camptocamp",
    "depends": [
        # OCA/agreement
        "agreement_repair",
        # OCA/field-service
        "fieldservice_agreement",
        "fieldservice_repair",
    ],
    "website": "https://github.com/OCA/field-service",
    "installable": True,
}
