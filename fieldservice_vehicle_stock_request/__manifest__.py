# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Vehicles - Stock Request',
    'summary': 'Link Stock Requests with Field Service Vehicle Inventory',
    'version': '12.0.2.0.0',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Brian McMaster, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_vehicle_stock',
        'fieldservice_stock_request',
        'fieldservice_delivery',
    ],
    'data': [
        'views/fsm_order.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
    ],
}
