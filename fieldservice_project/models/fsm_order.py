# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    project_id = fields.Many2one("project.project", string="Project", tracking=True)
    project_task_id = fields.Many2one(
        "project.task", string="Project Task", tracking=True
    )

    def action_view_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when viewing an FSM Order from a project.
        """
        action = self.env.ref("fieldservice.action_fsm_operation_order").read()[0]
        order = self.env["fsm.order"].search([("id", "=", self.id)])
        action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
        action["res_id"] = order.id
        return action

    @api.onchange("team_id")
    def onchange_team_id(self):
        self.project_id = self.team_id.project_id
