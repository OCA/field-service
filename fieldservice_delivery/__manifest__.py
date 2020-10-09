# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - Delivery',
    'summary': 'Delivery and Carriers for Field Services',
    'version': '11.0.0.0.1',
    'category': 'Field Service',
    'author': "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_stock',
        'delivery',
    ],
    'data': [
        'views/fsm_order.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
    ],
}
