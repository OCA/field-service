# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    change_log_count = fields.Integer(
        compute="_compute_change_log_count", string="# Change Logs"
    )
    change_log_ids = fields.One2many("change.log", "location_id", string="Change Logs")

    def _compute_change_log_count(self):
        for location in self:
            res = self.env["change.log"].search_count(
                [("location_id", "=", location.id)]
            )
            location.change_log_count = res or 0

    def action_open_change_logs(self):
        for location in self:
            vals = {
                "name": _("Change Logs"),
                "view_mode": "tree,form",
                "res_model": "change.log",
                "type": "ir.actions.act_window",
            }

            change_log_ids = self.env["change.log"].search(
                [("location_id", "=", location.id)]
            )
            if len(change_log_ids) > 1:
                vals["domain"] = [("id", "in", change_log_ids.ids)]
                vals["views"] = [
                    (
                        self.env.ref(
                            "fieldservice_change_management.change_log_view_list"
                        ).id,
                        "tree",
                    ),
                    (
                        self.env.ref(
                            "fieldservice_change_management.change_log_view_form"
                        ).id,
                        "form",
                    ),
                ]
            elif len(change_log_ids) == 1:
                vals["views"] = [
                    (
                        self.env.ref(
                            "fieldservice_change_management.change_log_view_form"
                        ).id,
                        "form",
                    )
                ]
                vals["res_id"] = change_log_ids.ids[0]
            return vals
