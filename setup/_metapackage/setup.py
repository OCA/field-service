import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_territory',
        'odoo13-addon-fieldservice',
        'odoo13-addon-fieldservice_crm',
        'odoo13-addon-fieldservice_recurring',
        'odoo13-addon-fieldservice_vehicle',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
