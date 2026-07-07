# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Subcontracting",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "license": "AGPL-3",
    "summary": "Auto-create Purchase Orders when FSOs are assigned to "
    "subcontractor workers",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "fieldservice_project",
        "fieldservice_timesheet",
        "fieldservice_stage_server_action",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/server_action_data.xml",
        "wizards/fsm_order_cancel_confirm_views.xml",
        "wizards/fsm_order_reassign_confirm_views.xml",
        "views/res_partner_views.xml",
        "views/fsm_template_views.xml",
        "views/fsm_order_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["edescalona"],
}
