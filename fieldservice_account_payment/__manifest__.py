# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Accounting Payment',
    'summary': 'This module allows the worker to accept payments during'
    ' his work at the location.',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_account',
    ],
    'data': [
        'views/fsm_order.xml',
        'views/account_payment_view.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
    ],
}
