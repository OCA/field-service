# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_vehicle_id = fields.Many2one("fsm.vehicle", string="Vehicle")

    def _action_done(self):
        """Verify that any pickings with an operation type which requires
        loading onto a FSM Vehicle have a vehicle assigned
        """
        res = {}
        for rec in self:
            if rec.picking_type_id.fsm_vehicle_in:
                if rec.fsm_vehicle_id:
                    picking = rec.with_context(vehicle_id=rec.fsm_vehicle_id.id)
                    res = super(StockPicking, picking)._action_done()
                else:
                    raise UserError(
                        _("You must provide the vehicle for this picking type.")
                    )
            res = super(StockPicking, rec)._action_done()
        return res

    def prepare_fsm_values(self, fsm_order):
        res = {}
        if fsm_order:
            res.update(
                {
                    "fsm_vehicle_id": fsm_order.vehicle_id.id or False,
                }
            )
        return res

    def write(self, vals):
        if vals.get("fsm_order_id", False):
            fsm_order = self.env["fsm.order"].browse(vals.get("fsm_order_id"))
            vals.update(self.prepare_fsm_values(fsm_order))
        return super().write(vals)
