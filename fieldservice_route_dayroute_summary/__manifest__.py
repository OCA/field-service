# Copyright 2026 Antoni Marroig (APSL-Nagarro) <antoni.marroig@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Day Route Summary",
    "summary": "Loading and delivery sheet for field service day routes",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["peluko00"],
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_sale_stock",
        "fieldservice_route",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_route_dayroute_templates.xml",
        "report/fsm_route_dayroute_report.xml",
        "views/fsm_route_dayroute_views.xml",
    ],
}
