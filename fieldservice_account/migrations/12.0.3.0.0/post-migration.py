# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("""INSERT INTO
    fsm_order_account_invoice_rel(fsm_order_id, invoice_id)
    SELECT DISTINCT l.fsm_order_id, l.invoice_id
    FROM account_invoice_line AS l
    WHERE l.fsm_order_id IS NOT NULL AND l.invoice_id IS NOT NULL;
    """)
