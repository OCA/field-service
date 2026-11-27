# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_vehicle_id = fields.Many2one(
        "fsm.vehicle",
        string="Vehicle",
        compute="_compute_fsm_vehicle_id",
        store=True,
        readonly=False,
    )

    @api.depends("fsm_order_id.vehicle_id")
    def _compute_fsm_vehicle_id(self):
        """Take the vehicle of the FSM order of the transfer, however the
        order is set on it (procurement, sale order, user)."""
        for rec in self:
            if rec.state in ("done", "cancel"):
                continue
            rec.fsm_vehicle_id = rec.fsm_order_id.vehicle_id or rec.fsm_vehicle_id

    def _is_vehicle_picking(self):
        self.ensure_one()
        return (
            self.picking_type_id.fsm_vehicle_in or self.picking_type_id.fsm_vehicle_out
        )

    def _check_and_update_vehicle_storage(self):
        """Ensure a vehicle is set for the picking type and update its storage."""
        for rec in self.filtered(lambda p: p._is_vehicle_picking()):
            if not rec.fsm_vehicle_id:
                raise UserError(
                    _("You must provide the vehicle for this picking type.")
                )
            rec.update_vehicle_storage()

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

    def write(self, vals):
        res = super().write(vals)
        if vals.get("fsm_vehicle_id"):
            self.update_vehicle_storage()
        return res

    def update_vehicle_storage(self):
        """Update the transfer's source or destination location to
        the FSM Vehicle's storage location depending on the operation type"""
        vehicle_parent_location = self.env.ref(
            "fieldservice_vehicle_stock.stock_location_vehicle"
        )
        for picking in self.filtered(
            lambda x: x._is_vehicle_picking() and x.state not in ["done", "cancel"]
        ):
            vehicle_location = (
                picking.fsm_vehicle_id.inventory_location_id or picking.location_dest_id
            )
            if not (vehicle_location.parent_path or "").startswith(
                vehicle_parent_location.parent_path
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
                picking.write({"location_dest_id": vehicle_location.id})
                picking.move_line_ids.write({"location_dest_id": vehicle_location.id})

            # Handle fsm_vehicle_out: Transferring from vehicle
            else:
                if vehicle_location == picking.location_id:
                    continue
                picking.write({"location_id": vehicle_location.id})
                picking.move_line_ids.write({"location_id": vehicle_location.id})
