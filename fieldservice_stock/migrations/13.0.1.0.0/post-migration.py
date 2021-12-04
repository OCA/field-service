# Copyright (C) 2021 Open Source Integrators
from openupgradelib import openupgrade


def update_warehouse_id_in_res_territory(cr):
    """
    Model fsm.territory is renamed with res.territory.
    Therefore, warehouse_id in res.territory won't have old data.
    This method will update warehouse_id in res_territory table.
    """
    openupgrade.logged_query(
        cr,
        """update res_territory set warehouse_id=f.warehouse_id
        from  fsm_territory f where f.id=res_territory.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    update_warehouse_id_in_res_territory(cr)
