from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "res_company", "order_prio0_request_late"):
        openupgrade.rename_columns(
            env.cr,
            {
                "res_company": [
                    ("order_prio0_request_late", "fsm_order_request_late_lowest")
                ],
            },
        )

    if openupgrade.column_exists(env.cr, "res_company", "order_prio1_request_late"):
        openupgrade.rename_columns(
            env.cr,
            {
                "res_company": [
                    ("order_prio1_request_late", "fsm_order_request_late_low")
                ],
            },
        )
    if openupgrade.column_exists(env.cr, "res_company", "order_prio2_request_late"):
        openupgrade.rename_columns(
            env.cr,
            {
                "res_company": [
                    ("order_prio2_request_late", "fsm_order_request_late_medium")
                ],
            },
        )
    if openupgrade.column_exists(env.cr, "res_company", "order_prio3_request_late"):
        openupgrade.rename_columns(
            env.cr,
            {
                "res_company": [
                    ("order_prio3_request_late", "fsm_order_request_late_high")
                ],
            },
        )
