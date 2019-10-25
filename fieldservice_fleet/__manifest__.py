# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Fleet',
    'summary': 'Link Field Service vehicles with Odoo Fleet',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author':
        'Brian McMaster, '
        'Open Source Integrators, '
        'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_vehicle',
        'fleet',
    ],
    'data': [
        'views/fsm_vehicle.xml',
        'views/fleet_vehicle.xml',
        'wizard/fsm_fleet_wizard.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
        'brian10048',
    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
}
