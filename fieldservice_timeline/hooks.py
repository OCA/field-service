# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def uninstall_hook(cr, registry):
    cr.execute(
        "UPDATE ir_act_window "
        "SET view_mode=replace(view_mode, ',timeline', '')"
        "WHERE view_mode LIKE '%,timeline%';"
    )
    cr.execute(
        "UPDATE ir_act_window "
        "SET view_mode=replace(view_mode, 'timeline,', '')"
        "WHERE view_mode LIKE '%timeline,%';"
    )
