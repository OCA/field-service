# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Route Availability",
    "summary": "Restricts blackout days for Scheduled Start (ETA) "
    "orders with the same date.",
    "version": "17.0.1.1.0",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_availability",
    ],
    "data": [
        "views/fsm_route.xml",
        "views/fsm_blackout_day_templates.xml",
    ],
}
