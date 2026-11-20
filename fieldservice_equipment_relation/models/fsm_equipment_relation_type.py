# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipmentRelationType(models.Model):
    _name = "fsm.equipment.relation.type"
    _description = "Field Service Equipment Relation Type"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    inverse_name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        ondelete="restrict",
    )
    relation_ids = fields.One2many(
        "fsm.equipment.relation", "relation_type_id", string="Relations"
    )
    relation_count = fields.Integer(compute="_compute_relation_count")

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique(code, company_id)",
            "The relation type code must be unique per company.",
        ),
    ]

    def _compute_relation_count(self):
        counts = dict(
            self.env["fsm.equipment.relation"]._read_group(
                [("relation_type_id", "in", self.ids)],
                ["relation_type_id"],
                ["__count"],
            )
        )
        for record in self:
            record.relation_count = counts.get(record, 0)

    def action_view_relations(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice_equipment_relation.action_fsm_equipment_relation"
        )
        action["domain"] = [("relation_type_id", "=", self.id)]
        action["context"] = {"default_relation_type_id": self.id}
        return action
