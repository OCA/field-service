# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMTranslation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("ar_001")
        cls.env.ref("base.module_fieldservice")._update_translations(["ar_001"])

    def test_configuration_fields_are_translatable(self):
        fields_by_model = {
            "fsm.category": ("name", "description"),
            "fsm.stage": ("name", "description", "legend_priority"),
            "fsm.tag": ("name",),
            "fsm.team": ("name", "description"),
            "fsm.template": ("name", "instructions"),
            "fsm.order.type": ("name",),
        }
        for model_name, field_names in fields_by_model.items():
            for field_name in field_names:
                self.assertTrue(
                    self.env[model_name]._fields[field_name].translate,
                    f"{model_name}.{field_name} must be translatable",
                )

    def test_seeded_configuration_has_arabic_names(self):
        expected_names = {
            "fieldservice.fsm_stage_new": "جديد",
            "fieldservice.fsm_stage_completed": "مكتمل",
            "fieldservice.fsm_stage_cancelled": "ملغى",
            "fieldservice.fsm_team_default": "الفريق الافتراضي",
            "fieldservice.fsm_order_type_inspection": "معاينة",
            "fieldservice.fsm_order_type_installation": "تركيب",
            "fieldservice.fsm_order_type_maintenance": "صيانة",
        }
        for xml_id, expected_name in expected_names.items():
            self.assertEqual(
                self.env.ref(xml_id).with_context(lang="ar_001").name,
                expected_name,
            )
