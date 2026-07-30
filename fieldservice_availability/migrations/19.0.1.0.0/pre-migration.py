from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Drop this constraint because,
    # `fieldservice_route_availability` is merging into `fieldservice_availability`.
    # Added new constraint : `_unique_blackout_day_zip` uniqueness of both data & zip
    openupgrade.delete_sql_constraint_safely(
        env, "fieldservice_availability", "fsm_blackout_day", "unique_blackout_day"
    )
