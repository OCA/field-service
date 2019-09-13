# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Location Builder',
    'summary': 'Adds a tool to help build out Location Hierarchies',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice'
    ],
    'data': [
        'wizard/fsm_location_builder_wizard.xml',
        'views/fsm_location_level.xml'
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'osi-scampbell',
        'max3903',
    ],
}
