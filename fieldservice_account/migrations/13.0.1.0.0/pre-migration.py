# Copyright (C) 2020 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_table_renames = [
    ("fsm_order_account_invoice_rel", "fsm_order_account_move_rel"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renames)
