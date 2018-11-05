# -*- coding: utf-8 -*-
# License AGPL-3

def uninstall_hook(cr, registry):
    cr.execute("UPDATE ir_act_window "
               "SET view_mode=replace(view_mode, ',map', '')"
               "WHERE view_mode LIKE '%,map%';")
    cr.execute("UPDATE ir_act_window "
               "SET view_mode=replace(view_mode, 'map,', '')"
               "WHERE view_mode LIKE '%map,%';")
    cr.execute("DELETE FROM ir_act_window "
               "WHERE view_mode = 'map';")
