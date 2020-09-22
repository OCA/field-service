# Copyright 2020 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fieldservice Mgmtsystem Nonconformity',
    'summary': """
        Bridge module between Field Service and Non Conformities""",
    'version': '12.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/field-service',
    'depends': [
        'fieldservice',
        'mgmtsystem_nonconformity',
    ],
    'data': [
        'views/mgmtsystem_nonconformity.xml',
    ],
}
