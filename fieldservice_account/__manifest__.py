# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Accounting',
    'summary': 'Track employee time and invoice for Field Service Orders',
    'version': '12.0.2.0.1',
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
        'data/time_products.xml',
        'data/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/fsm_person.xml',
        'views/account_invoice_view.xml',
        'views/hr_timesheet.xml'
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'osimallen',
    ],
}
