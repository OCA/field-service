# Copyright 2021 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, "fsm_territory"):
        openupgrade.rename_models(cr, [("fsm.territory", "res.territory")])
        openupgrade.rename_tables(cr, [("fsm_territory", "res_territory")])
