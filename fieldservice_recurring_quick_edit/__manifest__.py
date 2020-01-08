# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Recurring Quick edit',
    'summary': 'Add frequency quick edition on recurring order',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author':
        'Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice_recurring',
    ],
    'data': [
        'views/fsm_frequency.xml',
        'views/fsm_recurring.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
 }
