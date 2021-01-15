# Copyright 2020 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _field_type_change(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["account.move.line"],
        "account_move_line",
        "fsm_order_ids",
        openupgrade.get_legacy_name("fsm_order_id"),
    )


@openupgrade.migrate()
def migrate(env, version):
    _field_type_change(env)
