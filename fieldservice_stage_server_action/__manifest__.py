# Copyright (C) 2019 Open Source Integrators
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'FSM Stage Server Action',
    'summary': 'Add Server Actions based on FSM Stage',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/ursais/osi-addons',
    'depends': [
        'fieldservice',
        'fieldservice_substatus',
        'base_automation'
    ],
    'data': [
        'data/ir_server_action.xml',
        'data/fsm_stage.xml',
        'data/base_automation.xml',
        'views/fsm_stage.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
        'osi-scampbell'
    ]
}
