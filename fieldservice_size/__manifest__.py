# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Sizes",
    "summary": "Manage Sizes for Field Service Locations and Orders",
    "version": "16.0.1.0.0",
    "category": "Field Service",
    "author": "Brian McMaster, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "uom",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_size.xml",
        "views/fsm_location.xml",
        "views/fsm_order.xml",
        "views/menu.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": [
        "brian10048",
    ],
}
