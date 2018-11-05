from odoo import fields, models


class ResConfigSettingsFsmTeam(models.TransientModel):
    _inherit = 'res.config.settings'

    module_fsm_support_ticket = fields.Boolean(
        string="Manage FSM Support Tickets",
        default=False
    )
    module_fsm_team_handler = fields.Boolean(
        string="Manage FSM Teams",
        default=False
    )
    module_fsm_task_handler = fields.Boolean(
        string="Manage Work-sets & work-items",
        default=False
    )
