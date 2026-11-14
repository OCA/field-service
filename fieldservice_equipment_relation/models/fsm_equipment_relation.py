# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMEquipmentRelation(models.Model):
    _name = "fsm.equipment.relation"
    _description = "Field Service Equipment Relation"
    _order = "date_start desc, id desc"

    equipment_id = fields.Many2one(
        "fsm.equipment",
        string="Equipment",
        required=True,
        index=True,
        ondelete="cascade",
    )
    related_equipment_id = fields.Many2one(
        "fsm.equipment",
        string="Related Equipment",
        required=True,
        index=True,
        ondelete="cascade",
    )
    relation_type_id = fields.Many2one(
        "fsm.equipment.relation.type",
        string="Relation Type",
        required=True,
        index=True,
        ondelete="restrict",
    )
    relation_name = fields.Char(related="relation_type_id.name", store=True)
    inverse_relation_name = fields.Char(
        related="relation_type_id.inverse_name", store=True
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    active = fields.Boolean(default=True)
    notes = fields.Html()
    company_id = fields.Many2one(
        "res.company",
        related="equipment_id.company_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "equipment_relation_uniq",
            "unique(equipment_id, related_equipment_id, relation_type_id)",
            "This equipment relation already exists.",
        ),
        (
            "equipment_relation_not_self",
            "check(equipment_id != related_equipment_id)",
            "An equipment cannot be related to itself.",
        ),
    ]

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if (
                record.date_start
                and record.date_end
                and record.date_end < record.date_start
            ):
                raise ValidationError(
                    _("The end date cannot be before the start date.")
                )

    @api.constrains("equipment_id", "related_equipment_id")
    def _check_companies(self):
        for record in self:
            if (
                record.equipment_id.company_id
                and record.related_equipment_id.company_id
                and record.equipment_id.company_id
                != record.related_equipment_id.company_id
            ):
                raise ValidationError(
                    _(
                        "Equipment relations must link equipment from the same "
                        "company."
                    )
                )

    def action_open_equipment(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Equipment",
            "res_model": "fsm.equipment",
            "view_mode": "form",
            "res_id": self.equipment_id.id,
        }

    def action_open_related_equipment(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Related Equipment",
            "res_model": "fsm.equipment",
            "view_mode": "form",
            "res_id": self.related_equipment_id.id,
        }
