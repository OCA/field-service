import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-fieldservice',
        'odoo11-addon-fieldservice_account',
        'odoo11-addon-fieldservice_agreement',
        'odoo11-addon-fieldservice_delivery',
        'odoo11-addon-fieldservice_distribution',
        'odoo11-addon-fieldservice_maintenance',
        'odoo11-addon-fieldservice_partner_multi_relation',
        'odoo11-addon-fieldservice_recurring',
        'odoo11-addon-fieldservice_repair',
        'odoo11-addon-fieldservice_sale',
        'odoo11-addon-fieldservice_skill',
        'odoo11-addon-fieldservice_stock',
        'odoo11-addon-fieldservice_substatus',
        'odoo11-addon-fieldservice_vehicle',
        'odoo11-addon-fieldservice_vehicle_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
