# Copyright (C) 2022, Brian McMater
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

column_renames = {
    "fsm_order": [
        ("sale_line_id", None),
        ("sale_id", None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
