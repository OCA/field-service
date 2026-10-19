# Copyright 2026 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    if openupgrade.column_exists(cr, "fsm_delivery_time_range", "route_id"):
        # 1. Migrate the primary time range per route into the new inline fields.
        cr.execute("""
            UPDATE fsm_route fr
            SET default_start_time = tr.start_time,
                default_end_time = tr.end_time,
                has_default_schedule = TRUE
            FROM (
                SELECT DISTINCT ON (route_id) route_id, start_time, end_time
                FROM fsm_delivery_time_range
                WHERE route_id IS NOT NULL
                ORDER BY route_id, sequence ASC
            ) AS tr
            WHERE fr.id = tr.route_id
        """)

        # 2. Delete old route-bound time ranges.
        cr.execute("""
            DELETE FROM fsm_delivery_time_range
            WHERE route_id IS NOT NULL
        """)

        # 3. Safely drop the obsolete route_id column.
        openupgrade.drop_columns(cr, [("fsm_delivery_time_range", "route_id")])
