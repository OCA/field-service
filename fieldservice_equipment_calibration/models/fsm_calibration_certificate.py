# Copyright (C) 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmCalibrationCertificate(models.Model):
    _name = "fsm.calibration.certificate"
    _description = "Calibration Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    initial_date = fields.Date(tracking=True)
    expiration_date = fields.Date(tracking=True)
    notes = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        compute="_compute_company_id",
        store=True,
        readonly=False,
        precompute=True,
        required=True,
        index=True,
    )
    fsm_equipment_id = fields.Many2one(
        "fsm.equipment", string="Equipment", tracking=True, check_company=True
    )
    certificate_file = fields.Binary(tracking=True, attachment=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("fsm_equipment_id")
    def _compute_company_id(self):
        for rec in self:
            rec.company_id = (
                rec.fsm_equipment_id.company_id or rec.company_id or self.env.company
            )
