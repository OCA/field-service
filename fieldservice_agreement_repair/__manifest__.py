# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Agreement Repair",
    "summary": "Fieldservice Agreement Repair",
    "category": "Field Service",
    "version": "18.0.1.0.0",
    "author": "Camptocamp SA, Italo Lopes, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "maintainers": ["imlopes", "ivantodorovich"],
    "depends": [
        # OCA/agreement
        "agreement_repair",
        # OCA/field-service
        "fieldservice_agreement",
        "fieldservice_repair",
    ],
    "auto_install": True,
}
