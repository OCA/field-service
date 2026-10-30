# Copyright (C) 2026 Mr Abdulkarim M. Mousa
# @ Valutoria L.T.D. <abdulkarim@valutoria.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    district_id = fields.Many2one("res.district", string="District")
    region_id = fields.Many2one("res.region", string="Region")

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.state_id and self.state_id.country_id != self.country_id:
            self.state_id = False
            self.region_id = False
            self.district_id = False
        return {"domain": {"state_id": [("country_id", "=", self.country_id.id)]}}

    @api.onchange("state_id")
    def _onchange_state_id(self):
        if self.region_id and self.region_id.state_id != self.state_id:
            self.region_id = False
            self.district_id = False
        return {"domain": {"region_id": [("state_id", "=", self.state_id.id)]}}

    @api.onchange("region_id")
    def _onchange_region_id(self):
        if self.district_id and self.district_id.region_id != self.region_id:
            self.district_id = False
        return {"domain": {"district_id": [("region_id", "=", self.region_id.id)]}}

    @api.model
    def _normalize_territory_values(self, vals):
        values = dict(vals)
        district = (
            self.env["res.district"].browse(values["district_id"]).exists()
            if values.get("district_id")
            else self.env["res.district"]
        )
        region = (
            self.env["res.region"].browse(values["region_id"]).exists()
            if values.get("region_id")
            else self.env["res.region"]
        )
        state = (
            self.env["res.country.state"].browse(values["state_id"]).exists()
            if values.get("state_id")
            else self.env["res.country.state"]
        )

        if district:
            region = district.region_id
        if region:
            state = region.state_id
        if state:
            values["country_id"] = state.country_id.id
        if region:
            values["state_id"] = state.id
            values["region_id"] = region.id
        if district:
            values["district_id"] = district.id
        return values

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(
            [self._normalize_territory_values(vals) for vals in vals_list]
        )

    def write(self, vals):
        values = self._normalize_territory_values(vals)
        return super().write(values)

    @api.constrains("district_id", "region_id", "state_id", "country_id")
    def _check_territory_consistency(self):
        for partner in self:
            if (
                partner.district_id
                and partner.district_id.region_id != partner.region_id
            ):
                raise ValidationError(
                    self.env._("The district must belong to the selected region.")
                )
            if partner.region_id and partner.region_id.state_id != partner.state_id:
                raise ValidationError(
                    self.env._("The region must belong to the selected state.")
                )
