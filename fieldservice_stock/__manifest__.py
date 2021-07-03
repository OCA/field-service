# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Stock',
    'summary': 'Integrate the logistics operations with Field Service',
    'version': '12.0.3.0.1',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Brian McMaster, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/fsm_stock_data.xml',
        'views/fsm_territory.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/stock.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'brian10048',
        'wolfhall',
        'max3903',
        'smangukiya',
    ],
}
