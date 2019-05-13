# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Sales',
    'version': '12.0.1.0.1',
    'summary': 'Sales integration for Field Service',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'fieldservice_recurring',
        'sale_management',
    ],
    'data': [
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/fsm_recurring.xml',
        'views/product.xml',
        'views/sale_order.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
        'brian10048',
    ],
    'installable': True,
}
