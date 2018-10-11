# -*- coding: utf-8 -*-
{
    'name': "FS Task Handler",
    'summary': """
        Handle tasks to be executed during the lifetime of some project.""",
    'description': """
        Handles work orders, work sets and jobs.
    """,
    'author': "redO2oo.ch2",
    'website': "https://www.redo2oo.ch",
    'category': 'Field Service',
    'version': '11.0.1.0.0',
    'depends': [
        'red_team_handler',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/stage_data.xml',
        'views/fs_stages.xml',
        'views/fs_stage_set.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
}
