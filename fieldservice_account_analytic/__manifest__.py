# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Analytic Accounting',
    'summary': """Track analytic accounts on Field Service locations
                  and orders""",
    'version': '12.0.3.0.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_account',
        'analytic',
        'product',
    ],
    'data': [
        'data/ir_rule.xml',
        'security/ir.model.access.csv',
        'report/fsm_order_report_template.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
    ],
    'demo': [
        'demo/fsm_location.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'osimallen',
        'brian10048',
        'bodedra',
    ],
}
