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
        'odoo13-addon-fieldservice_account',
        'odoo13-addon-fieldservice_activity',
        'odoo13-addon-fieldservice_crm',
        'odoo13-addon-fieldservice_fleet',
        'odoo13-addon-fieldservice_geoengine',
        'odoo13-addon-fieldservice_partner_fax',
        'odoo13-addon-fieldservice_project',
        'odoo13-addon-fieldservice_purchase',
        'odoo13-addon-fieldservice_recurring',
        'odoo13-addon-fieldservice_route',
        'odoo13-addon-fieldservice_sale',
        'odoo13-addon-fieldservice_skill',
        'odoo13-addon-fieldservice_stage_server_action',
        'odoo13-addon-fieldservice_stage_validation',
        'odoo13-addon-fieldservice_stock',
        'odoo13-addon-fieldservice_vehicle',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
