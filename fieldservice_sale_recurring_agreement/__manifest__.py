# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Sale Recurring Agreement",
    "summary": "Fieldservice Sale Recurring Agreement",
    "category": "Field Service",
    "version": "17.0.1.0.0",
    "author": "Camptocamp SA, Italo Lopes, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainer": "Camptocamp, imlopes",
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
}
