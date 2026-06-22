from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    fsm_notification_user_id = fields.Many2one(
        "res.users",
        string="User who will receive notifications of FSM Orders created from POS",
    )
