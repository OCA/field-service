{
    "name": "Field Service - Portal",
    "version": "17.0.1.1.0",
    "summary": """
    Bridge module between fieldservice and portal.
    """,
    "depends": [
        "fieldservice",
        "portal",
    ],
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev"],
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "security/portal_security.xml",
        "views/fsm_order_template.xml",
        "views/portal_template.xml",
        "views/fsm_stage.xml",
    ],
    "demo": [
        "demo/fsm_location_demo.xml",
        "demo/fsm_order_demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "fieldservice_portal/static/src/js/fsm_order_portal.js",
        ],
    },
    "installable": True,
    "application": False,
}
