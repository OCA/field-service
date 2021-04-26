# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    fsm_order_ids = fields.One2many(
        "fsm.order", "project_task_id", string="Service Orders"
    )

    def action_create_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when creating an FSM Order from a project.
        """
        action = self.env.ref("fieldservice.action_fsm_operation_order")
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result["context"] = {
            "default_project_id": self.project_id.id,
            "default_project_task_id": self.id,
            "default_location_id": self.project_id.fsm_location_id.id,
            "default_origin": self.name,
        }
        res = self.env.ref("fieldservice.fsm_order_form", False)
        result["views"] = [(res and res.id or False, "form")]
        return result
