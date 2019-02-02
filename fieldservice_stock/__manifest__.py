# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Stock',
    'summary': 'Inventory and Stock Operations for Field Services',
    'version': '11.0.0.2.0',
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
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/stock.xml',
        'views/fsm_equipment.xml',
        'views/product_template.xml',
        'views/stock_production_lot.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'brian10048',
        'wolfhall',
        'max3903',
        'smangukiya',
    ],
}
