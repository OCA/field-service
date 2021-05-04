# Copyright (C) 2020 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMOrder(models.Model):
    _name = 'fsm.order'
    _inherit = ['fsm.order', 'geo.optimize']

    def prepare_destinations(self):
        super().prepare_destinations()
        destinations = []
        for order in self:
            loc = order.location_id
            if loc:
                address = loc._display_address(True)
                address = address.replace(' ', '+').replace('\n', '+')
                destinations.append(address)
        return destinations
