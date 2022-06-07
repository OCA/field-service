# Copyright (C) 2022, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _link_fsm_sale_to_lines(env):
    """
    FSM Orders created from a Sale Order with product FSM Tracking = Sale
    were not previously linked to any sale order line(s).
    """
    sale_col_name = openupgrade.get_legacy_name("sale_id")
    env.cr.execute(
        """
        SELECT id, {sale_col}
        FROM fsm_order
        WHERE {sale_col} IS NOT NULL
        """.format(
            sale_col=sale_col_name
        )
    )
    res = env.cr.fetchall()
    for fsm_order_id, sale_id in res:
        lines = env["sale.order.line"].filtered(
            lambda l: l.order_id == sale_id
            and l.product_id.field_service_tracking == "sale"
            and not l.fsm_order_id
        )
        lines.write({"fsm_order_id": fsm_order_id})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["fsm.order"],
        "fsm_order",
        "sale_line_ids",
        openupgrade.get_legacy_name("sale_line_id"),
    )
    _link_fsm_sale_to_lines(env)
