# Copyright 2011-2012 Nicolas Bessi (Camptocamp SA)
# Copyright 2016 Yannick Payot (Camptocamp SA)
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

NUMBER_ATT = ["float", "integer", "integer_big"]


class GeoVectorLayer(models.Model):
    _inherit = "geoengine.vector.layer"

    @api.constrains("geo_repr", "attribute_field_id")
    def _check_geo_repr(self):
        for rec in self:
            if (
                rec.attribute_field_id
                and rec.attribute_field_id.ttype not in NUMBER_ATT
                and rec.model_id.name not in ["fsm.order", "fsm.location"]
                and rec.geo_field_id.model not in ["fsm.order", "fsm.location"]
            ):
                if (
                    rec.geo_repr == "colored"
                    and rec.classification != "unique"
                    or rec.geo_repr == "proportion"
                ):
                    raise ValidationError(
                        _(
                            "You need to select a numeric field",
                        )
                    )
