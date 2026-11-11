# Copyright 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.addons.base.tests.common import BaseCommon


class TestResConfigSettings(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_settings_view_fields_exist(self):
        view = self.env.ref("fieldservice.res_config_settings_view_form")
        result = self.env["res.config.settings"].get_views([[view.id, "form"]])
        arch = etree.fromstring(result["views"]["form"]["arch"])
        field_names = arch.xpath("//field/@name")
        models_fields = result["models"]["res.config.settings"]["fields"]
        missing = [name for name in field_names if name not in models_fields]
        self.assertFalse(missing)

    def test_legacy_timeline_setting_follows_module_flag(self):
        settings = self.env["res.config.settings"].create({})
        self.assertEqual(
            settings.module_fieldservice_web_timeline_view,
            settings.module_fieldservice_timeline,
        )
        settings.module_fieldservice_web_timeline_view = True
        self.assertTrue(settings.module_fieldservice_timeline)
        settings.module_fieldservice_web_timeline_view = False
        self.assertFalse(settings.module_fieldservice_timeline)
        classified = settings._get_classified_fields()
        self.assertNotIn(
            "fieldservice_web_timeline_view",
            classified["module"].mapped("name"),
        )

    def test_stale_timeline_settings_arch_still_loads(self):
        """Views saved before the module rename must not break Settings."""
        view = self.env.ref("fieldservice.res_config_settings_view_form")
        self.env.cr.execute(
            """
            UPDATE ir_ui_view
               SET arch_db = replace(
                   arch_db::text,
                   'module_fieldservice_timeline',
                   'module_fieldservice_web_timeline_view'
               )::jsonb
             WHERE id = %s
            """,
            (view.id,),
        )
        self.env.invalidate_all()
        self.env.registry.clear_cache()
        result = self.env["res.config.settings"].get_views([[view.id, "form"]])
        arch = result["views"]["form"]["arch"]
        fields = result["models"]["res.config.settings"]["fields"]
        self.assertIn("module_fieldservice_web_timeline_view", arch)
        self.assertIn("module_fieldservice_web_timeline_view", fields)
