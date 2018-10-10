def migrate(cr, version):
    cr.execute('ALTER TABLE website_support_ticket RENAME COLUMN ticket_number TO ticket_number_old')
