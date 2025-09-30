from openupgradelib import openupgrade


def migrate(cr, version):
    """Merge (old) fsm.order.repair_id into (new) repair_ids"""
    if not version:
        return

    openupgrade.logged_query(
        cr,
        """
        UPDATE
            repair_order ro
        SET
            fsm_order_id = fo.id
        FROM
            fsm_order fo
        WHERE
            fo.repair_id IS NOT NULL
            AND ro.id = fo.repair_id
        """,
    )
