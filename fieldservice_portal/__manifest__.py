{
    "name": "Field Service - Portal",
    "version": "16.0.1.0.0",
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
    ],
    "demo": [
        "demo/fsm_location_demo.xml",
        "demo/fsm_order_demo.xml",
    ],
    "installable": True,
    "application": False,
}
