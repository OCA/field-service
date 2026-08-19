# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreement Sale",
    "summary": "Agreement on sales",
    "version": "19.0.1.1.0",
    "category": "Contract",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/agreement",
    "license": "AGPL-3",
    "depends": ["sale_management", "agreement"],
    "data": [
        "security/ir.model.access.csv",
        "views/agreement_view.xml",
        "views/sale_order.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["alexis-via", "bealdav"],
    "installable": True,
}
