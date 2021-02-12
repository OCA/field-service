# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute(
        """INSERT INTO
    fsm_order_account_invoice_rel(fsm_order_id, move_id)
    SELECT DISTINCT l.fsm_order_id, l.move_id
    FROM account_move_line AS l
    WHERE l.fsm_order_id IS NOT NULL AND l.move_id IS NOT NULL;
    """
    )
