import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_territory>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_activity>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_calendar>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_crm>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_isp_flow>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_project>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_size>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_stage_server_action>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_stock>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_substatus>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
