# -*- coding: utf-8 -*-
{
    'name': "Red FSM Base",
    'summary': """
        An application to manage field system services
        """,
    'description': """
        An application to manage field system services
    """,
    'author': "redOoo",
    'website': "https://www.redo2oo.ch",
    'category': 'Field Service',
    'version': '11.0.1.0.0',
    'depends': [
        'base',
        'fieldservice'
    ],
    'external_dependencies': {'python': ['requests_oauthlib']},
    'data': [
        'views/views.xml'
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/*.xml',
    ],
}
