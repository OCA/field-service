def migrate(cr, version):
    cr.execute('SELECT id, ticket_number_old FROM website_support_ticket')
    # RUN THROUGH ALL TICKETS TO CONVERT NUMBERS INTO STRINGS
    for record_id, old_number in cr.fetchall():
        new_number = str(old_number)
        if new_number:
            cr.execute('UPDATE website_support_ticket SET ticket_number=%s WHERE id=%s',
                       (new_number, record_id))

    # SELECT MAX TICKET NUMBER TO UPDATE SEQUENCE
    cr.execute('SELECT max(ticket_number_old) FROM website_support_ticket')
    max_number = cr.fetchone()
    cr.execute("UPDATE ir_sequence SET number_next=%s WHERE code='website.support.ticket'", (max_number+1, ))

    # DROP AUXILIAR COLUMN
    cr.execute("ALTER TABLE website_support_ticket DROP COLUMN ticket_number_old")
