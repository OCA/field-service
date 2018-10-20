{
    'name': "FSM Support Tickets",
    'summary': """
        Handles support tickets.""",
    'author': "redO2oo.ch2",
    'website': "https://www.redo2oo.ch",
    'category': 'Field Service',
    'version': '11.0.1.0.0',
    'depends': [
        'web',
        'website'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/website.menu.csv',
        'data/notify_mail_template.xml',
        'wizard/mail_compose_wizard.xml',
        'views/fsm_website_templates.xml',
        'views/fsm_ticket_categ.xml',
        'views/fsm_ticket_view.xml',
        'views/ticket_notification.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
}
