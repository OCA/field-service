# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[("fsm_location", "Location")])
    fsm_location = fields.Boolean("Is a FS Location")
    fsm_person = fields.Boolean("Is a FS Worker")
    fsm_location_ids = fields.One2many(
        comodel_name="fsm.location",
        string="Related FS Location",
        inverse_name="partner_id",
        readonly=True,
    )
    service_location_id = fields.Many2one(
        "fsm.location", string="Primary Service Location"
    )
    owned_location_ids = fields.One2many(
        "fsm.location",
        "owner_id",
        string="Owned Locations",
        domain=[("parent_id", "=", False)],
    )
    owned_location_count = fields.Integer(
        compute="_compute_owned_location_count", string="# of Owned Locations"
    )

    def _compute_owned_location_count(self):
        for partner in self:
            partner.owned_location_count = self.env["fsm.location"].search_count(
                [("owner_id", "child_of", partner.id)]
            )

    def action_open_owned_locations(self):
        for partner in self:
            owned_location_ids = self.env["fsm.location"].search(
                [("owner_id", "child_of", partner.id)]
            )
            action = self.env.ref("fieldservice.action_fsm_location").sudo().read()[0]
            action["context"] = {}
            if len(owned_location_ids) > 1:
                action["domain"] = [("id", "in", owned_location_ids.ids)]
            elif len(owned_location_ids) == 1:
                action["views"] = [
                    (self.env.ref("fieldservice.fsm_location_form_view").id, "form")
                ]
                action["res_id"] = owned_location_ids.ids[0]
            return action

    def _create_missing_fsm_location(self):
        for rec in self:
            if rec.type != "fsm_location":
                continue
            if not rec.fsm_location_ids:
                self.env["fsm.wizard"].action_convert_location(rec)

    def write(self, vals):
        # OVERRIDE to create the fsm.location for partners of type = fsm_location
        res = super().write(vals)
        if "type" in vals:
            self._create_missing_fsm_location()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to create the fsm.location for partners of type = fsm_location
        records = super().create(vals_list)
        records._create_missing_fsm_location()
        return records
