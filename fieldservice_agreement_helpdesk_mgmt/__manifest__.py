# Copyright 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fieldservice Agreement Helpdesk Mgmt',
    'summary': """
        Create links between Field Service, Agreements, and Helpdesk""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'images': ['static/description/banner.png'],
    'depends': [
        "helpdesk_mgmt_fieldservice",
        "agreement_helpdesk_mgmt",
        "fieldservice_agreement"
    ],
    'data': [
        'views/helpdesk_ticket.xml',
    ],
}
