# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmStageHistory(models.Model):
    _name = "fsm.stage.history"
    _description = "FSM Stage History"

    order_id = fields.Many2one("fsm.order", string="FSM Order")
    start_datetime = fields.Datetime("Start Date&time")
    stage_id = fields.Many2one("fsm.stage", string="Stage")
    duration = fields.Float(string="Duration",)
    total_duration = fields.Float(string="Total Duration",)
