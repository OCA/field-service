{
    'name': "FSM Base",
    'summary': """Base module for field service management.""",
    'author': "redOoo.ch2",
    'website': "https://www.redo2oo.ch",
    'category': 'Field service',
    'version': '0.1',
    'depends': [
        'base',
        'mail',
        'fieldservice'
    ],
    'data': [
        'data/notify_mail_template.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/templates.xml',
        'wizard/mail_compose_wizard.xml'
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True
}
