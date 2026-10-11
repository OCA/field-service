# Copyright (C) 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmEquipment(models.Model):
    _inherit = "fsm.equipment"

    fsm_calibration_certificate_ids = fields.One2many(
        "fsm.calibration.certificate",
        "fsm_equipment_id",
        string="Calibration Certificates",
    )
