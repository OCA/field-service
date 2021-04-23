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
        'odoo14-addon-fieldservice_skill',
        'odoo14-addon-fieldservice_timeline',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
