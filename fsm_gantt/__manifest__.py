# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Gantt View',
    'summary': 'Orders, Timeline',
    'version': '11.0.0.0.1',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'web_timeline',
    ],
    'data': [
        'views/fsm_gantt_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'application': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
        'smangukiya',
    ],
}
