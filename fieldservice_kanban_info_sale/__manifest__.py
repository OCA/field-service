# Copyright 2025 Bernat Obrador (APSL-Nagarro)<bobrador@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Kanban Info Sale",
    "version": "15.0.1.0.0",
    "summary": "Display key sale information on Field Service Kanban cards.",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["BernatObrador"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fieldservice_sale", "account_payment_sale"],
    "data": ["views/fsm_order.xml"],
}
