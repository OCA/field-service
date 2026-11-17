# Copyright (C) 2021 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    env.cr.execute(
        "UPDATE ir_act_window "
        "SET view_mode=replace(view_mode, ',timeline', '')"
        "WHERE view_mode LIKE '%,timeline%';"
    )
    env.cr.execute(
        "UPDATE ir_act_window "
        "SET view_mode=replace(view_mode, 'timeline,', '')"
        "WHERE view_mode LIKE '%timeline,%';"
    )
    env["ir.actions.act_window"].invalidate_model(["view_mode"])
