import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
CONTROLLER_ROOT = MODULE_ROOT / "controllers"
VISIT_SCRIPT = MODULE_ROOT / "static" / "src" / "js" / "visit_portal.js"
VISIT_STYLES = MODULE_ROOT / "static" / "src" / "scss" / "visit_portal.scss"
BOOKING_TEMPLATES = (
    MODULE_ROOT / "views" / "visit_portal_template.xml",
    MODULE_ROOT / "views" / "requests_portal_template.xml",
    MODULE_ROOT / "views" / "installation_portal_template.xml",
)


def booking_source(template):
    source = template.read_text()
    if template == BOOKING_TEMPLATES[0]:
        for asset in (VISIT_SCRIPT, VISIT_STYLES):
            if asset.exists():
                source += "\n" + asset.read_text()
    return source


def visit_script_source():
    if VISIT_SCRIPT.exists():
        return VISIT_SCRIPT.read_text()
    return BOOKING_TEMPLATES[0].read_text()


class TestFrontendTemplateContracts(unittest.TestCase):
    def test_portal_settings_extend_fieldservice_app(self):
        source = (MODULE_ROOT / "views" / "res_config_settings.xml").read_text()

        self.assertIn(
            '<field name="inherit_id" ref="fieldservice.res_config_settings_view_form"/>',
            source,
        )
        self.assertIn(
            '<xpath expr="//app[@name=\'fieldservice\']" position="inside">', source
        )
        self.assertNotIn('name="fieldservice_portal"', source)

    def test_visit_styles_and_script_are_frontend_assets(self):
        template = BOOKING_TEMPLATES[0].read_text()
        manifest = (MODULE_ROOT / "__manifest__.py").read_text()

        self.assertNotIn("<style>", template)
        self.assertNotIn("<script>", template)
        self.assertNotIn(" style=", template)
        self.assertTrue(VISIT_SCRIPT.exists())
        self.assertTrue(VISIT_STYLES.exists())
        self.assertIn(
            '"fieldservice_portal/static/src/js/visit_portal.js"', manifest
        )
        self.assertIn(
            '"fieldservice_portal/static/src/scss/visit_portal.scss"', manifest
        )
        self.assertIn(
            'import { rpc } from "@web/core/network/rpc";', VISIT_SCRIPT.read_text()
        )
        self.assertIn(
            'if (!document.getElementById("vbf"))', VISIT_SCRIPT.read_text()
        )

    def test_booking_templates_have_no_swiper_dependency(self):
        for template in BOOKING_TEMPLATES:
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertNotIn("cdn.jsdelivr.net/npm/swiper", source)
                self.assertNotIn("new Swiper", source)
                self.assertNotIn("swiper-", source)

    def test_booking_templates_cover_backend_four_week_window(self):
        for template in BOOKING_TEMPLATES:
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertIn("var maxDays = 28;", source)

        visit_source = booking_source(BOOKING_TEMPLATES[0])
        self.assertTrue(
            "i <= maxDays" in visit_source or "i &lt;= maxDays" in visit_source
        )
        for template in BOOKING_TEMPLATES[1:]:
            with self.subTest(template=template.name):
                self.assertIn("i &lt;= maxDays", template.read_text())

    def test_booking_templates_use_odoo_rpc(self):
        for template in BOOKING_TEMPLATES:
            source = booking_source(template)
            with self.subTest(template=template.name):
                if template == BOOKING_TEMPLATES[0] and VISIT_SCRIPT.exists():
                    self.assertIn('import { rpc } from "@web/core/network/rpc";', source)
                else:
                    self.assertIn(
                        'odoo.loader.modules.get("@web/core/network/rpc")', source
                    )
                self.assertNotIn("JSON.stringify({jsonrpc", source)

    def test_booking_templates_do_not_inject_html(self):
        for template in BOOKING_TEMPLATES:
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertNotIn("innerHTML", source)
                self.assertIn("replaceChildren", source)

        visit_source = visit_script_source()
        self.assertNotIn("setContent(d.name)", visit_source)
        self.assertIn("if (!allRoutes.length) {", visit_source)

    def test_dragging_visit_marker_pins_location(self):
        visit_source = visit_script_source()
        drag_handler = visit_source.split(
            "marker.addListener('dragend', function(){", 1
        )[1].split("});", 1)[0]
        self.assertIn("locationPinned = true;", drag_handler)

    def test_booking_configuration_does_not_use_global_parameters(self):
        for controller in (
            CONTROLLER_ROOT / "_booking.py",
            CONTROLLER_ROOT / "visit_portal.py",
            CONTROLLER_ROOT / "requests_portal.py",
        ):
            with self.subTest(controller=controller.name):
                self.assertNotIn("ir.config_parameter", controller.read_text())

    def test_installation_button_uses_policy_release_helper(self):
        source = (MODULE_ROOT / "views" / "sale_order_portal_template.xml").read_text()
        self.assertIn("sale_order._is_installation_released()", source)

    def test_visit_submit_copy_has_phone_and_payment_paths(self):
        source = BOOKING_TEMPLATES[0].read_text()
        self.assertIn("Submit Booking Request", source)
        self.assertIn("Continue to Quotation and Payment", source)

    def test_booking_scripts_initialize_after_late_render(self):
        initializers = (
            "initVisitBooking",
            "initMaintenanceBooking",
            "initInstallationBooking",
        )
        sentinels = ("visitDistrictPrefix", "reqSubmitError", "instSubmitError")
        for template, initializer, sentinel in zip(
            BOOKING_TEMPLATES, initializers, sentinels
        ):
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertIn("document.readyState === 'loading'", source)
                self.assertIn(f"{initializer}();", source)
                self.assertIn(f"setTimeout({initializer}, 0);", source)
                self.assertIn("Initialized) return;", source)
                self.assertIn(f"document.getElementById('{sentinel}')", source)
                self.assertIn("catch (error)", source)
                self.assertIn("Initialized = false;", source)

    def test_visit_allows_manual_address_without_map_key(self):
        source = booking_source(BOOKING_TEMPLATES[0])
        self.assertIn("visitManualAddress", source)
        self.assertIn("enableManualLocationMode();", source)

    def test_booking_errors_render_inline_without_native_alerts(self):
        error_ids = ("visitInlineError", "reqInlineError", "instInlineError")
        for template, error_id in zip(BOOKING_TEMPLATES, error_ids):
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertNotIn("alert(", source)
                self.assertIn(f'id="{error_id}"', source)
                self.assertIn('role="alert"', source)
                self.assertIn('aria-live="polite"', source)
                self.assertIn(f"document.getElementById('{error_id}')", source)
                self.assertIn("data.error", source)

    def test_directional_button_icons_are_pinned_to_logical_edges(self):
        for template in BOOKING_TEMPLATES:
            source = booking_source(template)
            with self.subTest(template=template.name):
                self.assertIn("btn-edge-icon", source)
                self.assertIn("position: absolute", source)
                self.assertIn("inset-inline-start", source)
                self.assertIn('html[dir="rtl"]', source)
                self.assertIn("scaleX(-1)", source)

        visit_source = booking_source(BOOKING_TEMPLATES[0])
        self.assertIn("inset-inline-end", visit_source)
        self.assertIn("btn-edge-icon-end", visit_source)

    def test_visit_map_fallback_becomes_two_step_manual_address_flow(self):
        source = booking_source(BOOKING_TEMPLATES[0])
        controller = (CONTROLLER_ROOT / "visit_portal.py").read_text()

        self.assertIn('id="state_select"', source)
        self.assertIn('id="city_input"', source)
        self.assertIn("manualLocation = true", source)
        self.assertIn("manual-location-only", source)
        self.assertIn("vstep1').classList.add('d-none')", source)
        self.assertIn("state_id", source)
        self.assertIn("manual_location", source)
        self.assertIn("'states':", controller)
        self.assertIn("kw.get('state_id')", controller)
        self.assertIn("kw.get('manual_location')", controller)

    def test_manual_visit_persists_city_and_district(self):
        source = booking_source(BOOKING_TEMPLATES[0])
        controller = (CONTROLLER_ROOT / "visit_portal.py").read_text()

        self.assertIn("manual_city_input", source)
        self.assertIn("district_select", source)
        self.assertIn("district.region_id != region", controller)
        self.assertNotIn("location_partner_vals['district_id'] = False", controller)
        self.assertNotIn("vals['city'] = region.name", controller)

    def test_region_filter_initializes_district_select(self):
        source = visit_script_source()
        update_region_options = source.split(
            "function updateRegionOptions() {", 1
        )[1].split(
            "document.getElementById('state_select').addEventListener", 1
        )[0]

        self.assertIn(
            "var districtSelect = document.getElementById('district_select');",
            update_region_options,
        )

    def test_visit_address_step_uses_one_compact_note(self):
        source = BOOKING_TEMPLATES[0].read_text()
        self.assertNotIn("Verify the address details, make any necessary changes", source)
        self.assertNotIn("Enter the full address, including the district", source)
        self.assertIn(
            "Enter the complete service address so our team can confirm coverage and find your site.",
            source,
        )

    def test_portal_ships_arabic_base_and_locale_catalogs(self):
        for catalog_name in ("ar.po", "ar_001.po"):
            catalog = MODULE_ROOT / "i18n" / catalog_name
            self.assertTrue(catalog.exists(), catalog_name)
            source = catalog.read_text()
            self.assertIn('msgid "Book a Technical Visit"', source)
            self.assertIn('msgstr "حجز زيارة فنية"', source)

    def test_portal_translates_its_settings_strings(self):
        translations = {
            "Quotation Template": "قالب عرض السعر",
            "Confirmation Policy": "سياسة التأكيد",
            "Installation Scheduling": "جدولة التركيب",
            "Release Policy": "سياسة الإتاحة",
        }
        for catalog_name in ("ar.po", "ar_001.po"):
            source = (MODULE_ROOT / "i18n" / catalog_name).read_text()
            for msgid, msgstr in translations.items():
                with self.subTest(catalog=catalog_name, msgid=msgid):
                    self.assertIn(
                        f'msgid "{msgid}"\nmsgstr "{msgstr}"', source
                    )


if __name__ == "__main__":
    unittest.main()
