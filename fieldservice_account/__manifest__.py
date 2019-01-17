# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Accounting',
    'summary': 'Track employee time and invoice for Field Service Orders',
    'version': '11.0.0.0.1',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'hr_timesheet',
        'analytic',
        'account',
        'product',
    ],
    'data': [
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'data/time_products.xml',
        'views/account_invoice_view.xml',
    ],
    'application': False,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'osimallen',
    ],
}
