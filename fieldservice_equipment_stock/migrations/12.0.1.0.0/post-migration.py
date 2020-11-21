# Copyright (C) 2020, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""
        UPDATE stock_picking_type
        SET create_fsm_equipment = 'true'
        WHERE code = 'outgoing';
    """)
