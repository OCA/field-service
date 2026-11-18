# Copyright (C) 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons import base

if not any(
    view_type[0] == "dayroute_map" for view_type in base.models.ir_actions.VIEW_TYPES
):
    base.models.ir_actions.VIEW_TYPES.append(("dayroute_map", "Map"))


class IrUIView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(
        selection_add=[("dayroute_map", "Day Route Map")],
        ondelete={"dayroute_map": "cascade"},
    )

    def _is_qweb_based_view(self, view_type):
        if view_type == "dayroute_map":
            return True
        return super()._is_qweb_based_view(view_type)

    def _get_view_info(self):
        res = super()._get_view_info()
        res.update({"dayroute_map": {"icon": "fa fa-globe"}})
        return res
