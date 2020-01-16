# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class FSMLocationBuilderWizard(models.TransientModel):
    _inherit = 'fsm.location.builder.wizard'
    _description = 'FSM Location Stock Builder Wizard'

    @api.multi
    def create_sub_locations(self):
        levels = len(self.level_ids) - 1
        location = self.env['fsm.location'].\
            browse(self.env.context.get('active_id'))

        def build_location(parent, num):
            if self.level_ids[num].spacer:
                spacer = " " + self.level_ids[num].spacer + " "
            else:
                spacer = " "
            for lev_id in range(self.level_ids[num].start_number,
                                self.level_ids[num].end_number + 1):
                vals = self.prepare_fsm_location_values(location,
                                                        parent,
                                                        spacer,
                                                        lev_id,
                                                        num)
                new_location = self.env['fsm.location'].create(vals)
                if num < levels:
                    build_location(new_location, num + 1)
        build_location(location, 0)

    def prepare_fsm_location_values(self, location, parent,
                                    spacer, lev_id, num):
        return {
            'name': self.
            level_ids[num].name + spacer + str(lev_id),
            'owner_id': location.owner_id.id,
            'fsm_parent_id': parent.id,
            'inventory_location_id': location.
            inventory_location_id.id
        }
