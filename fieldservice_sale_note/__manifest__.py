# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Sale Note",
    "summary": "Automatically copies the Internal Note from the Sale Order "
    "to the Resolution field in the Field Service Order",
    "version": "15.0.1.0.0",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_sale",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
}
