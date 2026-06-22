from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_notification_user_id = fields.Many2one(
        related="pos_config_id.fsm_notification_user_id", readonly=False
    )
