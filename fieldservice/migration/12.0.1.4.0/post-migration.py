# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # update new credit_product column with the tempory one
    cr.execute("""
               UPDATE fsm_order
               SET type = fsot.id
               FROM fsm_order_type as fsot
               WHERE UPPER(temporary_type) = UPPER(fsot.name)""")
    # Drop temporary column
    cr.execute('ALTER TABLE fsm_order DROP COLUMN temporary_type')
