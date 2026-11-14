# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    relation_ids = fields.One2many(
        "fsm.equipment.relation", "equipment_id", string="Relations"
    )
    inverse_relation_ids = fields.One2many(
        "fsm.equipment.relation",
        "related_equipment_id",
        string="Inverse Relations",
    )
    relation_count = fields.Integer(compute="_compute_relation_count")

    def _compute_relation_count(self):
        relation_model = self.env["fsm.equipment.relation"]
        counts = dict(
            relation_model._read_group(
                [
                    "|",
                    ("equipment_id", "in", self.ids),
                    ("related_equipment_id", "in", self.ids),
                ],
                ["equipment_id"],
                ["__count"],
            )
        )
        inverse_counts = dict(
            relation_model._read_group(
                [("related_equipment_id", "in", self.ids)],
                ["related_equipment_id"],
                ["__count"],
            )
        )
        for record in self:
            record.relation_count = counts.get(record, 0) + inverse_counts.get(
                record, 0
            )

    def action_view_relations(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice_equipment_relation.action_fsm_equipment_relation"
        )
        action["domain"] = [
            "|",
            ("equipment_id", "=", self.id),
            ("related_equipment_id", "=", self.id),
        ]
        action["context"] = {"default_equipment_id": self.id}
        return action
