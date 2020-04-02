# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Field Service Route Stock',
    'version': '12.0.1.2.1',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'stock_account',
        'fieldservice_route_vehicle',
        'fieldservice_vehicle_stock',
        'stock_location_limit_product',
    ],
    'data': [
        'views/fsm_route.xml',
        'views/fsm_route_dayroute.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
    ],
}
