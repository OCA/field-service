# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMVehicle(models.Model):
    _inherit = "fsm.vehicle"
    _inherits = {"fleet.vehicle": "fleet_vehicle_id"}

    fleet_vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle Details",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "fsm_vehicle_fleet_uniq",
            "unique(id,fleet_vehicle_id)",
            "FSM vehicle can only be linked to one fleet vehicle",
        )
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            fleet_id = vals.get("fleet_vehicle_id")
            if fleet_id:
                if vals.get("person_id", False):
                    vals["driver_id"] = vals.get("person_id")
                vals["is_fsm_vehicle"] = True
        return super(FSMVehicle, self).create(vals_list)

    def write(self, vals):
        # update fsm.vehicle worker based on the fleet.vehicle driver
        if "driver_id" in vals:
            for vehicle in self:
                if vehicle.is_fsm_vehicle:
                    vehicle.fleet_vehicle_id.set_fsm_driver()
        # update fleet.vehicle driver based on the fsm.vehicle worker
        fsm_worker_id = vals.get("person_id", False)
        if fsm_worker_id:
            worker_partner = self.env["fsm.person"].browse(fsm_worker_id).partner_id
            vals.update({"driver_id": worker_partner.id})
        return super().write(vals)
