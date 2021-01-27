# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Signature",
    "summary": "This module will provide signature link from FSM order.",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "category": "Field Service",
    "author": "Open Source Integrators",
    "website": "https://github.com/ursais/osi-addons",
    "depends": ["fieldservice", "sign"],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_order.xml",
        "views/sign_request.xml",
        "wizard/sign_send_request_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
    "installable": True
}
