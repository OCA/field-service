# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    @api.model
    def _default_sub_stage(self):
        return self.env["fsm.stage.status"].search([("name", "=", "Default")])

    sub_stage_id = fields.Many2one(
        "fsm.stage.status",
        string="Default Sub-Status",
        store=True,
        default=_default_sub_stage,
    )
    sub_stage_ids = fields.Many2many(
        "fsm.stage.status",
        "fsm_sub_stage_rel",
        "fsm_stage_id",
        "sub_stage_id",
        string="Potential Sub-Statuses",
        compute="_compute_sub_stage_ids",
    )

    @api.depends("sub_stage_id")
    def _compute_sub_stage_ids(self):
        for record in self:
            if record.sub_stage_id:
                record.sub_stage_ids = [(6, 0, [record.sub_stage_id.id])]
