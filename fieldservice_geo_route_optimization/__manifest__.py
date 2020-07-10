# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Field Service Geo Route Optimization',
    'summary': 'Optimize driving routes between records',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Brian McMaster, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'base_geo_route_optimization',
    ],
    'data': [
        'wizard/geo_route_orders_wizard_view.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'brian10048',
    ],
}
