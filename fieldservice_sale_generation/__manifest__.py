# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Generate Sale Orders",
    "summary": "Generate Sale Orders from a Field Service Order",
    "version": "12.0.1.0.0",
    "category": "Field Service",
    "website": "https://www.github.com/OCA/field-service.git",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice",
        "sale",
    ],
    "data": [
        # "views/sale_order_views.xml",
        "views/fsm_order_views.xml",
    ],
}
