# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""UPDATE stock_picking_type
                SET require_vehicle_id = True
                WHERE name in ('Vehicle Loading', 'Vehicle Returns',
                               'Location Pickup', 'Location Delivery');
    """)
