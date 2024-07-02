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
        'odoo-addon-fieldservice_account>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_account_analytic>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_account_payment>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_activity>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_calendar>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_change_management>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_crm>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_delivery>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_distribution>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_equipment_stock>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_fleet>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_isp_account>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_isp_flow>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_location_builder>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_logbook>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_partner_multi_relation>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_project>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_purchase>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_recurring>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_repair>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_route>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_sale>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_sale_recurring>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_sale_stock>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_size>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_skill>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_stage_server_action>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_stage_validation>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_stock>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_substatus>=15.0dev,<15.1dev',
        'odoo-addon-fieldservice_vehicle>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
