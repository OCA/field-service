# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Route',
    'summary': 'Manage Field Service Day Route based on Assigned Workers in Orders',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_substatus',
    ],
    'data': [
        'data/fsm_stage_status.xml',
        'data/fsm_stage.xml',
        'views/fsm_route_view.xml',
        'views/res_config_settings.xml',
        'views/fsm_person_view.xml',
    ],
    'application': True,
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
    ],
}
