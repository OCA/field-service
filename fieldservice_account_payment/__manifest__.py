# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Field Service - Accounting Payment',
    'summary': 'Allow workers to collect payments from the order.',
    'version': '12.0.1.1.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fsm_order.xml',
        'views/account_payment.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Production/Stable',
    'maintainers': ['max3903'],
}
