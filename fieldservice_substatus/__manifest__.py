# Copyright (C) 2018 - TODAY, Open Source Integrators, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Sub-Status',
    'summary': 'Sub-statuses for Field Service Orders',
    'version': '11.0.0.0.1',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Brian McMaster, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fsm_stage_status.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
        'brian10048',
    ],
}
