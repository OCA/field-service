# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Maintenance',
    'summary': 'Integrate Field Service orders with maintenance requests',
    'version': '12.0.1.2.1',
    'category': 'Field Service',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'maintenance',
    ],
    'data': [
        'data/fsm_order_type.xml',
        'views/maintenance_equipment_view.xml',
        'views/maintenance_request_view.xml',
        'views/fsm_equipment_view.xml',
        'views/fsm_order_view.xml',
        'wizard/maintenance_equipment_wizard.xml'
    ],
    'pre_init_hook': 'pre_init_hook',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'smangukiya',
        'max3903',
        'bodedra',
    ],
    'installable': True,
}
