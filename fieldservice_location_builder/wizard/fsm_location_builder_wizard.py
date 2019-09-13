# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMLocationBuilderWizard(models.TransientModel):
    _name = 'fsm.location.builder.wizard'
    _description = 'FSM Location Builder Wizard'
    level_ids = fields.One2many('fsm.location.level',
                                'wizard_id', string="Level ID's")

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
                tags = self.level_ids[num].tag_ids.ids
                vals = {'name': self.level_ids[num].
                        name + spacer + str(lev_id),
                        'owner_id': location.owner_id.id,
                        'customer_id': location.customer_id.id,
                        'fsm_parent_id': parent.id,
                        'street': location.street,
                        'street2':  self.level_ids[num].
                        name + spacer + str(lev_id),
                        'city': location.city,
                        'zip': location.zip,
                        }
                if tags:
                    vals.update({
                        'category_id': [(6, 0, tags)]
                    })

                if location.state_id:
                    vals.update([('state_id', location.state_id.id)])
                if location.country_id:
                    vals.update([('country_id', location.country_id.id)])
                if location.territory_id:
                    vals.update([('territory_id', location.territory_id.id)])
                if location.tz:
                    vals.update([('tz', location.tz.id)])

                new_location = self.env['fsm.location'].create(vals)
                if num < levels:
                    build_location(new_location, num + 1)
        build_location(location, 0)
