# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Vehicles - Stock",
    "summary": "Track inventory of Field Service vehicles",
    "version": "15.0.1.0.0",
    "category": "Field Service",
    "author": "Open Source Integrators, "
    "Brian McMaster, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_vehicle",
        "fieldservice_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/fsm_stock_data.xml",
        "views/fsm_vehicle.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": [
        "brian10048",
        "wolfhall",
        "max3903",
    ],
}
