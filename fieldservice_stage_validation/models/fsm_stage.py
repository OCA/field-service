# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

STAGE_TYPE_TO_MODEL = {
    "order": "fsm.order",
    "equipment": "fsm.equipment",
    "location": "fsm.location",
    "worker": "fsm.person",
}


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    validate_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields to Validate",
        help="Select fields which must be set on the document in this stage",
    )
    stage_type_model_name = fields.Char(
        compute="_compute_stage_model",
        string="Model for Stage",
        help="Technical field to hold model type",
    )

    @api.depends("stage_type")
    def _compute_stage_model(self):
        for rec in self:
            rec.stage_type_model_name = STAGE_TYPE_TO_MODEL.get(rec.stage_type)
