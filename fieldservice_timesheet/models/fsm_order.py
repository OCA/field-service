# Copyright 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    project_id = fields.Many2one("project.project", string="Project", tracking=True)
    project_task_id = fields.Many2one(
        "project.task", string="Project Task", tracking=True
    )
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="fsm_order_id",
        string="Timesheet",
    )
