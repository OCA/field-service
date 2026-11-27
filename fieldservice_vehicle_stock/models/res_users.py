# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models

FSM_VEHICLE_STOCK_ACCESS = (
    "fieldservice_vehicle_stock.access_stock_picking_fsm_user",
    "fieldservice_vehicle_stock.access_stock_move_fsm_user",
)


class ResUsers(models.Model):
    _inherit = "res.users"

    def _fsm_vehicle_stock_unrestricted(self, model_name):
        """Whether the user may write ``model_name`` through an access right
        other than the FSM user ones of this module.

        Used by the vehicle transfer record rules: only the rights granted
        here are limited to the vehicle operation types.
        """
        self.ensure_one()
        own_ids = [
            access.id
            for access in (
                self.env.ref(xmlid, raise_if_not_found=False)
                for xmlid in FSM_VEHICLE_STOCK_ACCESS
            )
            if access
        ]
        return bool(
            self.env["ir.model.access"]
            .sudo()
            .search_count(
                [
                    ("model_id.model", "=", model_name),
                    ("perm_write", "=", True),
                    ("id", "not in", own_ids),
                    "|",
                    ("group_id", "=", False),
                    ("group_id", "in", self.groups_id.ids),
                ],
                limit=1,
            )
        )
