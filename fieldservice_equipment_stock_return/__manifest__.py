# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Stock Equipment Return",
    "summary": "Integrate return orders for field service equipments",
    "version": "17.0.1.0.0",
    "category": "Field Service",
    "author": "Camptocamp, " "Italo LOPES, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_equipment_stock",
    ],
    "data": [
        "data/fsm_order_type.xml",
        "views/fsm_equipment.xml",
        "views/fsm_order_view.xml",
        "views/fsm_order_type_view.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": [
        "brian10048",
        "wolfhall",
        "max3903",
        "smangukiya",
        "imlopes",
    ],
}
