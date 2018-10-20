{
    'name': "FS Task Handler",
    'summary': """
        Handle tasks to be executed during the lifetime of some project.""",
    'author': "redO2oo.ch2",
    'website': "https://www.redo2oo.ch",
    'category': 'Field Service',
    'version': '11.0.1.0.0',
    'depends': [
        'fieldservice'
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
