# Copyright (C) 2019 - TODAY, Open Source Integrators, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Sub-Status',
    'summary': 'Add sub-statuses to Field Service orders',
    'version': '12.0.1.1.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, '
              'Brian McMaster, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
    ],
    'data': [
        'data/fsm_stage_status.xml',
        'data/fsm_stage.xml',
        'security/ir.model.access.csv',
        'views/fsm_stage_status.xml',
        'views/fsm_stage.xml',
        'views/fsm_order.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
        'brian10048',
        'bodedra'
    ],
}
