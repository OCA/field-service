# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    is_a_distribution = fields.Boolean(string="Is a Distribution")
    dist_parent_id = fields.Many2one("fsm.location", string="Distribution Parent")

    distrib_count = fields.Integer(
        compute="_compute_distrib_sublocation_ids",
        string="# of distributed sub-locations",
    )

    def _compute_distrib_sublocation_ids(self):
        for location in self:
            location.distrib_count = self.env["fsm.location"].search_count(
                [
                    ("dist_parent_id", "=", location.id),
                    ("id", "!=", location.id),
                    ("is_a_distribution", "=", True),
                ]
            )

    def action_view_distrib_sublocation(self):
        """
        This function returns an action that display existing
        distribution sub-locations of a given fsm location id.
        It can either be a in a list or in a form view, if there is only one
        sub-location to show.
        """
        for location in self:
            action = self.env.ref("fieldservice.action_fsm_location").read()[0]
            sublocation = self.env["fsm.location"].search(
                [
                    ("dist_parent_id", "=", location.id),
                    ("id", "!=", location.id),
                    ("is_a_distribution", "=", True),
                ]
            )
            if len(sublocation) == 1:
                action["views"] = [
                    (
                        self.env.ref("fieldservice." + "fsm_location_form_view").id,
                        "form",
                    )
                ]
                action["res_id"] = sublocation.id
            else:
                action["domain"] = [
                    ("id", "in", sublocation.ids),
                    ("is_a_distribution", "=", True),
                ]
            return action
