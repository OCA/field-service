# Copyright (C) 2022 - TODAY, Rafnix Guzmán
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    def to_controller_url(self):
        if self.id and self.lot_id:
            serial = self.lot_id.name
            return {
                "type": "ir.actions.act_url",
                "url": "/equipment/%s" % (serial),
                "target": "new",
            }
