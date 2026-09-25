# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    # Migrate data from obsolete route_id column to the new Many2many relation table
    if openupgrade.column_exists(cr, "fsm_delivery_time_range", "route_id"):
        cr.execute("""
            CREATE TABLE IF NOT EXISTS fsm_route_delivery_time_range_rel (
                route_id INTEGER NOT NULL,
                time_range_id INTEGER NOT NULL,
                CONSTRAINT fsm_route_delivery_time_range_rel_pk
                    PRIMARY KEY (route_id, time_range_id)
            )
            """)

        cr.execute("""
            INSERT INTO fsm_route_delivery_time_range_rel (route_id, time_range_id)
            SELECT route_id, id
            FROM fsm_delivery_time_range
            WHERE route_id IS NOT NULL
            ON CONFLICT DO NOTHING
            """)
