# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Accounting',
    'summary': 'Track invoices linked to Field Service orders',
    'version': '12.0.2.0.1',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/fsm_order_report_template.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/fsm_person.xml',
        'views/fsm_route.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
        'demo/fsm_location.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['osimallen'],
    'pre_init_hook': 'pre_init_hook',
}
