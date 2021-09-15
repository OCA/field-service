# Copyright (C) 2018, Open Source Integrators
# Copyright 2020 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def update_fsm_order_in_aml(cr):
    """ Update fsm_order_id in account.move.line to use in post migration """
    openupgrade.logged_query(
        cr,
        """
            ALTER TABLE account_move_line ADD COLUMN fsm_order_id INTEGER
        """,
    )
    openupgrade.logged_query(
        cr,
        """update account_move_line
        set
            fsm_order_id=ail.fsm_order_id
        from
            account_invoice_line ail
        where
            ail.id=account_move_line.old_invoice_line_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_fsm_order_in_aml(env.cr)
