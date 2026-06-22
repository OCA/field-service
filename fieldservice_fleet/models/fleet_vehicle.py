# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    is_fsm_vehicle = fields.Boolean(string="Is used for Field Service?")

    def set_fsm_driver(self):
        for record in self.filtered("is_fsm_vehicle").filtered("driver_id"):
            driver_partner = record.driver_id
            fsm_worker = self.env["fsm.person"].search(
                [("partner_id", "=", driver_partner.id)], limit=1
            )
            if not fsm_worker:
                # Create FSM worker
                fsm_worker = self.env["fsm.person"].create(
                    {"partner_id": driver_partner.id}
                )
                driver_partner.fsm_person = True
            fsm_vehicle = self.env["fsm.vehicle"].search(
                [("fleet_vehicle_id", "=", record.id)], limit=1
            )
            # Assign the worker to the FSM vehicle
            fsm_vehicle.person_id = fsm_worker.id
