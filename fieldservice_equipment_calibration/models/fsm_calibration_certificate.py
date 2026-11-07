# Copyright (C) 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmCalibrationCertificate(models.Model):
    _name = "fsm.calibration.certificate"
    _description = "Calibration Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    initial_date = fields.Date(tracking=True)
    expiration_date = fields.Date(tracking=True)
    notes = fields.Text()
    fsm_equipment_id = fields.Many2one(
        "fsm.equipment", string="Equipment", tracking=True
    )
    certificate_file = fields.Binary(tracking=True, attachment=True)
    active = fields.Boolean(default=True, tracking=True)
