# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Stock',
    'summary': 'Integrate the logistics operations with Field Service',
    'version': '12.0.1.1.0',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Brian McMaster, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'stock_request_direction',
        'stock_request_picking_type',
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
        'views/stock_request.xml',
        'views/stock_request_order.xml',
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
