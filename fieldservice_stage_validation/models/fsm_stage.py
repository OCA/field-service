# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    validate_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields to Validate",
        help="Select fields which must be set on the document in this stage",
    )

    stage_type_model_id = fields.Many2one(
        "ir.model",
        compute="_compute_stage_model",
        string="Model for Stage",
        help="Technical field to hold model type",
    )

    @api.depends("stage_type")
    def _compute_stage_model(self):
        Model = self.env["ir.model"]
        for rec in self:
            model_id = False
            if rec.stage_type:
                model_string = "fsm." + rec.stage_type
                model_id = Model.search([("model", "=", model_string)], limit=1).id
            rec.stage_type_model_id = model_id
