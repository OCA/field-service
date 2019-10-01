# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service - CRM',
    'version': '12.0.1.0.1',
    'summary': 'CRM Opportunity integration for Field Service',
    'category': 'Field Service',
    'author': 'Patrick Wilson, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'crm',
    ],
    'data': [
        'views/crm_lead.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'patrickrwilson',
    ],
    'installable': True,
}
