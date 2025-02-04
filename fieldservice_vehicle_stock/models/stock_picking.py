# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_vehicle_id = fields.Many2one("fsm.vehicle", string="Vehicle")

    def _check_and_update_vehicle_storage(self):
        """Ensure a vehicle is assigned for the picking type and update its storage location"""
        for rec in self:
            if (
                rec.picking_type_id.fsm_vehicle_in
                or rec.picking_type_id.fsm_vehicle_out
            ):
                if rec.fsm_vehicle_id:
                    rec.update_vehicle_storage()
                    rec = rec.with_context(vehicle_id=rec.fsm_vehicle_id.id)
                else:
                    raise UserError(
                        _("You must provide the vehicle for this picking type.")
                    )

    def action_assign(self):
        """Verify that any pickings with an operation type which requires
        loading onto or unloading from a FSM Vehicle have a vehicle assigned
        and ensure the vehicle's storage location is correctly set before reserving
        stock to the picking
        """
        self._check_and_update_vehicle_storage()
        return super().action_assign()

    def _action_done(self):
        """Verify that any pickings with an operation type which requires
        loading onto or unloading from a FSM Vehicle have a vehicle assigned
        and ensure the vehicle's storage location is correctly set before
        completing the picking
        """
        self._check_and_update_vehicle_storage()
        return super()._action_done()

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
        res = super().write(vals)
        if vals.get("fsm_vehicle_id", False):
            self.update_vehicle_storage()
        return res

    def update_vehicle_storage(self):
        """Update the transfer's source or destination location to
        the FSM Vehicle's storage location depending on the operation type"""
        for picking in self.filtered(
            lambda x: (
                x.picking_type_id.fsm_vehicle_in or x.picking_type_id.fsm_vehicle_out
            )
            and x.state not in ["done", "cancel"]
        ):
            # Common validation for both 'vehicle in' and 'vehicle out'
            vehicle_location = (
                picking.fsm_vehicle_id.inventory_location_id or picking.location_dest_id
            )
            vehicle_parent_location = self.env.ref(
                "fieldservice_vehicle_stock.stock_location_vehicle"
            )
            if vehicle_location not in self.env["stock.location"].search(
                [("id", "child_of", vehicle_parent_location.id)]
            ):
                raise UserError(
                    _(
                        "The inventory location of the FSM vehicle must be a "
                        "descendant of the Vehicles location."
                    )
                )

            # Handle fsm_vehicle_in: Transferring to vehicle
            if picking.picking_type_id.fsm_vehicle_in:
                if vehicle_location == picking.location_dest_id:
                    continue
                # Update the destination location
                picking.write({"location_dest_id": vehicle_location.id})
                picking.move_line_ids.write({"location_dest_id": vehicle_location.id})

            # Handle fsm_vehicle_out: Transferring from vehicle
            elif picking.picking_type_id.fsm_vehicle_out:
                if vehicle_location == picking.location_id:
                    continue
                picking.write({"location_id": vehicle_location.id})
                picking.move_line_ids.write({"location_id": vehicle_location.id})
