from odoo import fields, models


class FsmLocation(models.Model):
    _inherit = "fsm.location"

    place = fields.Char()
