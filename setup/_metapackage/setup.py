import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_territory>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_account>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_activity>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_crm>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_project>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_sale>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_stock>=16.0dev,<16.1dev',
        'odoo-addon-fieldservice_vehicle>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
