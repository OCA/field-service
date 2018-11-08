{
    'name': "FSM Task Handler",
    'summary': """
        Handle tasks to be executed during the lifetime of some project.""",
    'author': "redO2oo.ch2",
    'website': "https://www.redo2oo.ch",
    'category': 'Field Service',
    'version': '11.0.1.0.0',
    'depends': [
        'fieldservice',
        'fsm_base',
        'fsm_team_handler'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/stage_data.xml',
        'views/fs_stages.xml',
        'views/fs_stage_set.xml',
        'wizard/reject_proposal.xml',
        'views/work_sets.xml',
        'views/work_item.xml',
        'views/work_set_forms.xml',
        'views/mail_notification.xml'
    ],
    'demo': [],
}
