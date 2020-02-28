# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class FSMLocationBuilderWizard(models.TransientModel):
    _inherit = 'fsm.location.builder.wizard'
    _description = 'FSM Location Analytic Builder Wizard'

    def prepare_fsm_location_values(self, location, parent,
                                    spacer, lev_id, num):
        vals = super().prepare_fsm_location_values(location, parent,
                                                   spacer, lev_id, num)
        if location.analytic_account_id:
            vals.update({'analytic_account_id': location.
                        analytic_account_id.id})
        return vals
