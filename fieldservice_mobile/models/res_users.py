# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def get_portal_config_values(self, config_parameters=[]):
        params_dict = {}
        for config_param in config_parameters:
            if config_param in [
                "fieldservice_mobile.fsm_allow_portal_view_move_qty",
                "fieldservice_mobile.fsm_allow_portal_update_move_qty",
                "fieldservice_mobile.fsm_allow_portal_validate_move_qty",
                "fieldservice_sale_order_line.fsm_allow_portal_view_sol_qty",
                "fieldservice_sale_order_line.fsm_allow_portal_update_sol_qty",
            ]:
                params = self.env["ir.config_parameter"].sudo()
                params_dict.update({
                    config_param: bool(params.get_param(config_param))
                    })
        return params_dict
