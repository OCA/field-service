# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""INSERT INTO fsm_order_account_invoice_rel
                SET (fsm_order_id, invoice_id) VALUES (
                SELECT fsm_order_id, id
                FROM account_invoice
                WHERE fsm_order_id IS NOT NULL);""")
