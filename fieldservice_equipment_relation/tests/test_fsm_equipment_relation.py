# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMEquipmentRelation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Equipment = cls.env["fsm.equipment"]
        cls.Relation = cls.env["fsm.equipment.relation"]
        cls.relation_type = cls.env["fsm.equipment.relation.type"].create(
            {
                "name": "Provides",
                "inverse_name": "Provided by",
                "code": "test_provides",
            }
        )
        cls.equipment = cls.Equipment.create({"name": "Test source equipment"})
        cls.related_equipment = cls.Equipment.create({"name": "Test related equipment"})

    def test_create_relation_and_smart_button(self):
        relation = self.Relation.create(
            {
                "equipment_id": self.equipment.id,
                "related_equipment_id": self.related_equipment.id,
                "relation_type_id": self.relation_type.id,
            }
        )
        self.assertEqual(self.equipment.relation_count, 1)
        self.assertEqual(self.related_equipment.relation_count, 1)
        self.assertEqual(self.equipment.relation_ids, relation)
        self.assertEqual(self.related_equipment.inverse_relation_ids, relation)
        self.assertEqual(
            self.equipment.action_view_relations()["domain"],
            [
                "|",
                ("equipment_id", "=", self.equipment.id),
                ("related_equipment_id", "=", self.equipment.id),
            ],
        )

    def test_cannot_relate_equipment_to_itself(self):
        with self.assertRaises(ValidationError):
            self.Relation.create(
                {
                    "equipment_id": self.equipment.id,
                    "related_equipment_id": self.equipment.id,
                    "relation_type_id": self.relation_type.id,
                }
            )

    def test_date_order(self):
        with self.assertRaises(ValidationError):
            self.Relation.create(
                {
                    "equipment_id": self.equipment.id,
                    "related_equipment_id": self.related_equipment.id,
                    "relation_type_id": self.relation_type.id,
                    "date_start": "2026-02-01",
                    "date_end": "2026-01-01",
                }
            )
