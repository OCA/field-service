from openupgradelib import openupgrade


def migrate(cr, version):
    """Merge (old) fsm.order.equipment_id into (new) equipment_ids"""
    if not version:
        return

    openupgrade.logged_query(
        cr,
        """
        INSERT INTO fsm_equipment_fsm_order_rel (fsm_order_id, fsm_equipment_id)
        SELECT
            o.id AS fsm_order_id,
            o.equipment_id
        FROM
            fsm_order o
        LEFT JOIN
            fsm_equipment_fsm_order_rel r
        ON
            r.fsm_order_id = o.id
            AND r.fsm_equipment_id = o.equipment_id
        WHERE
            o.equipment_id IS NOT NULL
            AND r.fsm_order_id IS NULL
        """,
    )
