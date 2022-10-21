# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _default_size_id(self):
        size = False
        if self.type:
            size = self.env["fsm.size"].search(
                [("type_id", "=", self.type.id), ("is_order_size", "=", True)], limit=1
            )
        return size

    def _default_size_value(self):
        size_value = 0
        if self.size_id:
            size = self.env["fsm.location.size"].search(
                [
                    ("location_id", "=", self.location_id.id),
                    ("size_id", "=", self.size_id.id),
                ],
                limit=1,
            )
            if size:
                size_value = size.quantity
        return size_value

    def _default_size_uom(self):
        return self.size_id.uom_id if self.size_id else False

    size_id = fields.Many2one("fsm.size", default=_default_size_id)
    size_value = fields.Float(string="Order Size", default=_default_size_value)
    size_uom = fields.Many2one(
        "uom.uom", string="Unit of Measure", default=_default_size_uom
    )

    @api.onchange("location_id")
    def _onchange_location_id_customer(self):
        res = super()._onchange_location_id_customer()
        self.size_id = self._default_size_id()
        self.size_value = self._default_size_value()
        self.size_uom = self._default_size_uom()
        return res

    @api.onchange("type")
    def onchange_type(self):
        self.size_id = self._default_size_id()
        self.size_value = self._default_size_value()
        self.size_uom = self._default_size_uom()

    @api.onchange("size_id")
    def onchange_size_id(self):
        self.size_value = self._default_size_value()
        self.size_uom = self._default_size_uom()
