# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields, models


class FSMActivity(models.Model):
    _name = "fsm.activity"
    _description = "Field Service Activity"

    name = fields.Char(
        "Name", required=True, readonly=True, states={"todo": [("readonly", False)]}
    )
    required = fields.Boolean(
        "Requireid",
        default=False,
        readonly=True,
        states={"todo": [("readonly", False)]},
    )
    sequence = fields.Integer("Sequence")
    completed = fields.Boolean("Completed", default=False)
    completed_on = fields.Datetime("Completed On", readonly=True)
    completed_by = fields.Many2one("res.users", "Completed By", readonly=True)
    ref = fields.Char(
        "Reference", readonly=True, states={"todo": [("readonly", False)]}
    )
    fsm_order_id = fields.Many2one("fsm.order", "FSM Order")
    fsm_template_id = fields.Many2one("fsm.template", "FSM Template")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Completed"), ("cancel", "Cancelled")],
        "State",
        readonly=True,
        default="todo",
    )

    def action_done(self):
        self.completed = True
        self.completed_on = datetime.now()
        self.completed_by = self.env.user
        self.state = "done"

    def action_cancel(self):
        self.state = "cancel"
