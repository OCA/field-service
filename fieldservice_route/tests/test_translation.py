# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFSMRouteTranslation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("ar_001")
        cls.env.ref("base.module_fieldservice")._update_translations(["ar_001"])
        cls.env.ref("base.module_fieldservice_route")._update_translations(["ar_001"])

    def test_route_name_is_translatable(self):
        self.assertTrue(self.env["fsm.route"]._fields["name"].translate)

    def test_seeded_route_stages_have_arabic_names(self):
        expected_names = {
            "fieldservice_route.fsm_stage_route_new": "جديد",
            "fieldservice_route.fsm_stage_route_close": "مغلق",
        }
        for xml_id, expected_name in expected_names.items():
            self.assertEqual(
                self.env.ref(xml_id).with_context(lang="ar_001").name,
                expected_name,
            )
