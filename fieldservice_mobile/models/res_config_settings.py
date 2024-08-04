# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_allow_portal_view_move_qty = fields.Boolean(
        string="Allow portal user to view stock move quantities",
        config_parameter="fieldservice_mobile.fsm_allow_portal_view_move_qty",
    )
    fsm_allow_portal_update_move_qty = fields.Boolean(
        string="Allow portal user update of stock move quantities",
        config_parameter="fieldservice_mobile.fsm_allow_portal_update_move_qty",
    )
