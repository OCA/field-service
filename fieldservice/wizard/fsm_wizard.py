# Copyright (C) 2018 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain


class FSMWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "fsm.wizard"
    _description = "FSM Record Conversion"

    fsm_record_type = fields.Selection(
        [("person", "Worker"), ("location", "Location")], "Record Type"
    )

    def action_convert(self):
        partners = self.env["res.partner"].browse(
            self.env.context.get("active_ids", [])
        )
        for partner in partners:
            if self.fsm_record_type == "person":
                self.action_convert_person(partner)
            if self.fsm_record_type == "location":
                self.action_convert_location(partner)
        return {"type": "ir.actions.act_window_close"}

    def _prepare_fsm_location(self, partner):
        owner = partner.parent_id or partner
        vals = {"partner_id": partner.id, "owner_id": owner.id}
        if partner.parent_id:
            parent_location = partner.parent_id.fsm_location_ids[:1]
            if parent_location:
                vals["parent_id"] = parent_location.id
        return vals

    def action_convert_location(self, partner):
        fl_model = self.env["fsm.location"]
        if fl_model.search_count(Domain("partner_id", "=", partner.id)) == 0:
            fl_model.create(self._prepare_fsm_location(partner))
            partner.write({"fsm_location": True, "type": "fsm_location"})
            self.action_other_address(partner)
        else:
            raise UserError(
                self.env._(
                    "A Field Service Location related to that partner already exists."
                )
            )

    def action_convert_person(self, partner):
        fp_model = self.env["fsm.person"]
        if fp_model.search_count(Domain("partner_id", "=", partner.id)) == 0:
            fp_model.create({"partner_id": partner.id})
            partner.write({"fsm_person": True})
        else:
            raise UserError(
                self.env._(
                    "A Field Service Worker related to that partner already exists."
                )
            )

    def action_other_address(self, partner):
        for child in partner.child_ids:
            child.type = "other"
