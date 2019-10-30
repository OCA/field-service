# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # Add temporary type column
    cr.execute('ALTER TABLE fsm_order ADD temporary_type VARCHAR(20)')
    # Store pre-migration type
    cr.execute('UPDATE fsm_order SET temporary_type = type')
