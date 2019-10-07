# Copyright (C) 2019 - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Contracts',
    'summary': 'Manage FSM Contracts',
    'author': 'Akretion, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'category': 'Field Service',
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'depends': [
        'contract',
        'fieldservice_sale',
        'fieldservice_recurring',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/contract.xml',
        'views/contract_line.xml',
        'views/fsm_recurring.xml',
        'views/fsm_order.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': [
        'hparfr',
    ],
}
