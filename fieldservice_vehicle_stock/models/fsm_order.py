# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("vehicle_id"):
            # the transfers take the vehicle of the order (computed field):
            # move their source or destination to its storage location now
            self.picking_ids.update_vehicle_storage()
        return res
