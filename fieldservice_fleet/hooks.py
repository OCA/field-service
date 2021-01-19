# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    # Check for existing fsm vehicles
    cr.execute("SELECT * FROM fsm_vehicle")
    vehicles = []
    vehicles = cr.dictfetchall()
    if vehicles:
        # Get a fleet vehicle model to set on the new Fleet vehicle(s)
        env = api.Environment(cr, SUPERUSER_ID, {})
        model_id = env["fleet.vehicle.model"].search([], limit=1).id
        # Create a new Fleet vehicle for each FSM vehicle
        for veh in vehicles:
            # Get the FSM worker to set as the Fleet driver
            fsm_person_id = veh.get("person_id", False)
            driver_id = False
            if fsm_person_id:
                driver_id = env["fsm.person"].browse(fsm_person_id).partner_id.id
            cr.execute(
                """
                        INSERT INTO fleet_vehicle (
                            name,
                            model_id,
                            driver_id,
                            is_fsm_vehicle,
                            odometer_unit,
                            active)
                        VALUES (
                            %s,
                            %s,
                            %s,
                            True,
                            'kilometers',
                            True);""",
                (veh.get("name"), model_id, driver_id),
            )
            # Set this new Fleet vehicle on the existing FSM vehicle
            cr.execute(
                """
                        SELECT id
                        FROM fleet_vehicle
                        ORDER BY id desc
                        LIMIT 1
                       """
            )
            fleet = cr.dictfetchone()
            cr.execute(
                """
                        UPDATE fsm_vehicle
                        SET fleet_vehicle_id = %s
                        WHERE id = %s;""",
                (fleet.get("id"), veh.get("id")),
            )
