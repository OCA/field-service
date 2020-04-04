# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Route Vehicle',
    'summary': 'This module allows you to set the vehicle'
    ' on the routes and day routes.',
    'version': '12.0.2.1.1',
    'category': 'Field Service',
    'license': 'AGPL-3',
    'author': "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_vehicle_stock',
        'fieldservice_route',
    ],
    'data': [
        'views/fsm_route.xml',
        'views/fsm_route_dayroute.xml',
    ],
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
    ],
    'installable': True,
    'auto_install': True,
}
