# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class FSMFleetWizard(models.TransientModel):
    """
    A wizard to convert a fleet.vehicle record to a fsm.vehicle
    """

    _name = "fsm.fleet.wizard"
    _description = "FSM Fleet Vehicle Conversion"

    def action_convert(self):
        vehicles = self.env["fleet.vehicle"].browse(self._context.get("active_ids", []))
        for vehicle in vehicles:
            self.action_convert_vehicle(vehicle)
        return {"type": "ir.actions.act_window_close"}

    def _prepare_fsm_vehicle(self, vehicle):
        return {
            "fleet_vehicle_id": vehicle.id,
            "name": vehicle.name,
        }

    def action_convert_vehicle(self, vehicle):
        res = self.env["fsm.vehicle"].search_count(
            [("fleet_vehicle_id", "=", vehicle.id)]
        )
        if res == 0:
            vals = self._prepare_fsm_vehicle(vehicle)
            self.env["fsm.vehicle"].create(vals)
            vehicle.write({"is_fsm_vehicle": True})
            vehicle.set_fsm_driver()
        else:
            raise UserError(
                _(
                    "A Field Service Vehicle related to that"
                    " Fleet Vehicle already exists."
                )
            )
