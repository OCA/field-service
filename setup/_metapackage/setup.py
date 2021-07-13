import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_territory',
        'odoo14-addon-fieldservice',
        'odoo14-addon-fieldservice_account',
        'odoo14-addon-fieldservice_account_analytic',
        'odoo14-addon-fieldservice_agreement',
        'odoo14-addon-fieldservice_calendar',
        'odoo14-addon-fieldservice_crm',
        'odoo14-addon-fieldservice_distribution',
        'odoo14-addon-fieldservice_isp_account',
        'odoo14-addon-fieldservice_isp_flow',
        'odoo14-addon-fieldservice_partner_multi_relation',
        'odoo14-addon-fieldservice_project',
        'odoo14-addon-fieldservice_route',
        'odoo14-addon-fieldservice_sale',
        'odoo14-addon-fieldservice_skill',
        'odoo14-addon-fieldservice_stock',
        'odoo14-addon-fieldservice_timeline',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
