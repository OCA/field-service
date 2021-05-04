# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class FSMLocationBuilderWizard(models.TransientModel):
    _inherit = 'fsm.location.builder.wizard'
    _description = 'FSM Location Stock Builder Wizard'

    def prepare_fsm_location_values(self, location, parent,
                                    spacer, lev_id, num):
        vals = super().prepare_fsm_location_values(location, parent,
                                                   spacer, lev_id, num)
        vals.update({'inventory_location_id': location.
                    inventory_location_id.id})
        return vals
