# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Field Service Recurring Work Orders',
    'summary': 'Manage recurring field service works',
    'version': '11.0.0.1.1',
    'category': 'Field Service',
    'author':
        'Brian McMaster, '
        'Open Source Integrators, '
        'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/recurring_security.xml',
        'views/fsm_frequency.xml',
        'views/fsm_frequency_set.xml',
        'views/fsm_recurring_template.xml',
        'views/fsm_recurring.xml',
        'data/recurring_cron.xml',
    ],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': [
        'wolfhall',
        'max3903',
        'brian10048',
    ],
}
