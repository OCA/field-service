import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-field-service",
    description="Meta package for oca-field-service Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-fieldservice',
        'odoo11-addon-fieldservice_agreement',
        'odoo11-addon-fieldservice_distribution',
        'odoo11-addon-fieldservice_skill',
        'odoo11-addon-fieldservice_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
