# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreements",
    "summary": "Adds an agreement object",
    "version": "19.0.2.2.0",
    "category": "Contract",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/agreement",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/agreement_security.xml",
        "security/ir.model.access.csv",
        "views/agreement.xml",
        "views/agreement_type.xml",
        "views/res_config_settings.xml",
        "views/agreement_menu.xml",
        "views/res_partner.xml",
    ],
    "demo": ["demo/demo.xml"],
    "development_status": "Beta",
    "maintainers": [
        "ygol",
        "alexis-via",
    ],
    "installable": True,
    "application": True,
}
