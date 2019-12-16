# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - ISP Accounting',
    'summary': """Invoice Field Service orders based on employee time
                  or contractor costs""",
    'version': '12.0.2.1.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_account_analytic',
        'hr_timesheet',
    ],
    'data': [
        'data/time_products.xml',
        'views/account.xml',
        'views/fsm_order.xml',
        'views/fsm_person.xml',
        'views/hr_timesheet.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'osimallen',
        'brian10048',
        'bodedra',
    ],
}
