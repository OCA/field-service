# Copyright (C) 2018 Open Source Integrators
from openupgradelib import openupgrade


def update_pricelist_in_res_branch(cr):
    """
    Model fsm.branch is renamed with res.branch.
    Therefore, pricelist_id in res.branch won't have old data.
    This method will update pricelist_id in res_branch table.
    """
    openupgrade.logged_query(
        cr,
        """update res_branch set pricelist_id=f.pricelist_id
        from  fsm_branch f where f.id=res_branch.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    update_pricelist_in_res_branch(cr)
