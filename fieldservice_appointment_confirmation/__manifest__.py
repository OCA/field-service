# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Appointment Confirmation",
    "summary": "Request, confirm and reschedule field service appointments "
    "with the customer through a secure tokenized link.",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "license": "AGPL-3",
    "depends": [
        "fieldservice",
        "mail",
        "resource",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/fsm_stage_views.xml",
        "views/fsm_order_views.xml",
        "wizard/fsm_appointment_confirmation_wizard_views.xml",
        "wizard/res_config_settings_views.xml",
        "templates/appointment_portal.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": [],
    "application": False,
}
