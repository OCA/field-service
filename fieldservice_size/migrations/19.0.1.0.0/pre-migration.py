from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "fsm.order",
                None,  # None because the field is not stored, so no DB column exists.
                "size_uom_category",
                "size_relative_uom_id",
            ),
        ],
    )
