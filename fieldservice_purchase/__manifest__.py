# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Purchase',
    'summary': 'Manage FSM Purchases',
    'author': 'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'category': 'Field Service',
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'depends': [
        'fieldservice',
        'purchase',
    ],
    'data': [
        'views/fsm_person.xml',
    ],
    'development_status': 'Beta',
    'maintainers': [
        'osi-scampbell',
    ],
}
