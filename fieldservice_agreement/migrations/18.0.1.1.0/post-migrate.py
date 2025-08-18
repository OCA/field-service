def migrate(cr, version):
    if not version:
        return

    cr.execute("""
            SELECT id, fsm_location_id
            FROM agreement
            WHERE fsm_location_id IS NOT NULL
        """)

    for agreement_id, location_id in cr.fetchall():
        cr.execute(
            """
                INSERT INTO agreement_fsm_location_rel (agreement_id, fsm_location_id)
                VALUES (%s, %s)
            """,
            (agreement_id, location_id),
        )
