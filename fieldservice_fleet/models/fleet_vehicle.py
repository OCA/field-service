# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    is_fsm_vehicle = fields.Boolean(string="Is used for Field Service?")

    def set_fsm_driver(self):
        self.ensure_one()
        if self.driver_id and self.is_fsm_vehicle:
            driver_partner = self.driver_id
            fsm_worker = self.env["fsm.person"].search(
                [("partner_id", "=", driver_partner.id)]
            )
            if not fsm_worker:
                # Create FSM worker
                fsm_worker = self.env["fsm.person"].create(
                    {"partner_id": driver_partner.id}
                )
                driver_partner.write({"fsm_person": True})
            fsm_vehicle = self.env["fsm.vehicle"].search(
                [("fleet_vehicle_id", "=", self.id)]
            )
            # Assign the worker to the FSM vehicle
            fsm_vehicle.person_id = fsm_worker
