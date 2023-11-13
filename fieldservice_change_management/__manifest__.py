# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Change Management",
    "summary": "Manage Change Logs on Locations",
    "author": "Pavlov Media, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Extra Tools",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "fieldservice",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/change_log_impact.xml",
        "data/change_log_stage.xml",
        "data/change_log_type.xml",
        "report/change_log_reports.xml",
        "views/change_log.xml",
        "views/change_log_impact.xml",
        "views/change_log_stage.xml",
        "views/change_log_tags.xml",
        "views/change_log_type.xml",
        "views/fsm_location.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["patrickrwilson"],
}
