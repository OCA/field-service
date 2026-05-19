# Copyright 2026 Binhex - Rolando Pérez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    fsm_order_properties = fields.Properties(
        "Properties",
        definition="team_id.fsm_order_properties_definition",
        copy=True,
    )

    @api.model
    def _add_missing_default_values(self, values):
        """Inject team_id before super so property defaults can be applied.

        fields.Properties._add_default_values() returns {} if team_id is
        absent from the defaults dict. Since team_id is computed with no
        default= callable, the ORM cannot infer it from create vals alone.

        Compute team_id from the location (if given) or from the standard
        default, then inject it so that _add_default_values can resolve the
        container and apply property defaults.
        """
        if "team_id" not in values:
            team = None
            if values.get("location_id"):
                location = self.env["fsm.location"].browse(values["location_id"])
                if location.team_id:
                    team = location.team_id
            if not team:
                team = self._default_team_id()
            if team:
                values = dict(values, team_id=team.id)
        return super()._add_missing_default_values(values)
