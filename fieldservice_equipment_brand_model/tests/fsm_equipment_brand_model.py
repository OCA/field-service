# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestFSMEquipmentBrandModel(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Equipment = self.env["fsm.equipment"]
        self.EquipmentBrand = self.env["fsm.equipment.brand"]
        self.EquipmentModel = self.env["fsm.equipment.model"]
        self.equipment = self.Equipment.create({"name": "Equipment"})
        self.equipment_brand = self.EquipmentBrand.create(
            {
                "name": "Equipment Brand",
                "code": "KO",
                "description": "Equipment Brand Description",
            }
        )
        self.equipment_model = self.EquipmentModel.create(
            {
                "name": "Equipment Model",
                "code": "UNI",
                "brand_id": self.equipment_brand.id,
                "description": "Equipment Model Description",
            }
        )

    def test_fsm_equipment_brand_model(self):
        self.equipment.write(
            {
                "brand_id": self.equipment_brand.id,
                "model_brand_id": self.equipment_model.id,
            }
        )
        self.assertEqual(self.equipment_brand, self.equipment.brand_id)
        self.assertEqual(self.equipment_model, self.equipment.model_brand_id)

    def test_fsm_equipment_onchange_brand_model(self):
        with Form(self.equipment) as equipment_form:
            equipment_form.brand_id = self.equipment_brand
            equipment_form.model_brand_id = self.equipment_model
        equipment_form.save()
        self.assertEqual(self.equipment.brand_id, self.equipment_brand)
        self.assertEqual(self.equipment.model_brand_id, self.equipment_model)
        equipment_brand_2 = self.EquipmentBrand.create(
            {
                "name": "Equipment Brand",
                "code": "KO",
                "description": "Equipment Brand Description",
            }
        )
        with Form(self.equipment) as equipment_form:
            equipment_form.brand_id = equipment_brand_2
        equipment_form.save()
        self.assertFalse(self.equipment.model_brand_id)

    def test_fsm_equipment_constraint_brand_model(self):
        equipment_brand_2 = self.EquipmentBrand.create(
            {
                "name": "Equipment Brand",
                "code": "KO",
                "description": "Equipment Brand Description",
            }
        )
        with self.assertRaisesRegex(
            ValidationError,
            "The brand of the model and equipment brand are not the same.",
        ):
            self.equipment.write(
                {
                    "brand_id": equipment_brand_2.id,
                    "model_brand_id": self.equipment_model.id,
                }
            )
