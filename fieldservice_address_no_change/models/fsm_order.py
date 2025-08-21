# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    territory_id = fields.Many2one(
        "res.territory",
        string="Territory",
        compute="_compute_location_id_fields",
        related="",
        store=True,
    )
    branch_id = fields.Many2one(
        "res.branch",
        string="Branch",
        compute="_compute_location_id_fields",
        related="",
        store=True,
    )
    district_id = fields.Many2one(
        "res.district",
        string="District",
        compute="_compute_location_id_fields",
        related="",
        store=True,
    )
    region_id = fields.Many2one(
        "res.region",
        string="Region",
        compute="_compute_location_id_fields",
        related="",
        store=True,
    )
    street = fields.Char(compute="_compute_location_id_fields", related="", store=True)
    street2 = fields.Char(compute="_compute_location_id_fields", related="", store=True)
    zip = fields.Char(compute="_compute_location_id_fields", related="", store=True)
    city = fields.Char(compute="_compute_location_id_fields", related="", store=True)
    state_name = fields.Char(
        string="State", compute="_compute_location_id_fields", related="", store=True
    )
    country_name = fields.Char(
        string="Country", compute="_compute_location_id_fields", related="", store=True
    )

    @api.depends(
        "location_id.territory_id",
        "location_id.branch_id",
        "location_id.district_id",
        "location_id.region_id",
        "location_id.street",
        "location_id.street2",
        "location_id.zip",
        "location_id.city",
        "location_id.state_id.name",
        "location_id.country_id.name",
    )
    def _compute_location_id_fields(self):
        for rec in self:
            if rec.location_id and rec.stage_id != self.env.ref(
                "fieldservice.fsm_stage_completed"
            ):
                rec.territory_id = rec.location_id.territory_id
                rec.branch_id = rec.location_id.branch_id
                rec.district_id = rec.location_id.district_id
                rec.region_id = rec.location_id.region_id
                rec.street = rec.location_id.street
                rec.street2 = rec.location_id.street2
                rec.zip = rec.location_id.zip
                rec.city = rec.location_id.city
                rec.state_name = rec.location_id.state_id.name or False
                rec.country_name = rec.location_id.country_id.name or False
