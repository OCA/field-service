# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Stock add-on',
    'summary': 'Inventory and Stock operations for Field Service',
    'version': '11.0.0.0.1',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Brian McMaster, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'base_geolocalize',
        'mail',
        'fieldservice',
        'stock',
    ],
    'data': [
        'data/fsm_stock_data.xml',
        'views/fsm_location.xml',
        'views/fsm_vehicle.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'brian10048',
        'wolfhall',
        'max3903',
    ],
}
