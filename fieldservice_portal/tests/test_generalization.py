from odoo.tests.common import TransactionCase, tagged
from odoo.tools import format_amount


@tagged("post_install", "-at_install")
class TestFieldServiceGeneralization(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.owner = cls.env["res.partner"].create({"name": "Generalization Owner"})
        location_partner = cls.env["res.partner"].create(
            {"name": "Generalization Site", "parent_id": cls.owner.id}
        )
        cls.location = cls.env["fsm.location"].create(
            {"partner_id": location_partner.id, "owner_id": cls.owner.id}
        )

    def test_order_type_behavior_survives_renaming(self):
        order_type = self.env["fsm.order.type"].create(
            {"name": "Any translated label", "service_type": "survey"}
        )
        order = self.env["fsm.order"].create(
            {"location_id": self.location.id, "type": order_type.id}
        )
        order_type.name = "Completely renamed"
        self.assertEqual(order._get_service_type(), "survey")

    def test_sale_template_behavior_survives_renaming(self):
        template = self.env["sale.order.template"].create(
            {"name": "Arbitrary label", "service_type": "maintenance"}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.owner.id,
                "sale_order_template_id": template.id,
            }
        )
        template.name = "Renamed template"
        self.assertEqual(order._get_service_type(), "maintenance")

    def test_stage_event_survives_renaming(self):
        stage = self.env["fsm.stage"].create(
            {
                "name": "Arbitrary stage label",
                "sequence": 47,
                "stage_type": "order",
                "notification_event": "started",
            }
        )
        stage.name = "Renamed stage"
        self.assertEqual(stage.notification_event, "started")

    def test_seeded_label_fields_support_record_translations(self):
        self.assertTrue(self.env["fsm.stage"]._fields["name"].translate)
        self.assertTrue(self.env["fsm.route"]._fields["name"].translate)
        self.assertTrue(self.env["sale.order.template"]._fields["name"].translate)

    def test_route_type_uses_english_translation_sources(self):
        selection = dict(
            self.env["fsm.route"]._fields["route_type"]._description_selection(
                self.env
            )
        )
        self.assertEqual(selection["visit"], "Site Visit")
        self.assertEqual(selection["maintenance"], "Maintenance")
        self.assertEqual(selection["installation"], "Installation")

    def test_amount_uses_order_currency(self):
        order = self.env["sale.order"].create({"partner_id": self.owner.id})
        self.assertEqual(
            order._formatted_amount(1234.5),
            format_amount(self.env, 1234.5, order.currency_id),
        )

    def test_base_url_has_no_customer_specific_fallback(self):
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param("web.base.url", "https://service.example.com/")
        self.assertEqual(
            self.env["fieldservice.notification"]._get_base_url(),
            "https://service.example.com",
        )

    def test_portal_configuration_defaults_and_settings_fields(self):
        company = self.env["res.company"].create({"name": "Portal Policy Company"})
        settings = self.env["res.config.settings"].with_company(company).create(
            {"company_id": company.id}
        )

        self.assertEqual(company.visit_confirmation_policy, "phone")
        self.assertEqual(company.installation_release_policy, "payment")
        for field_name in (
            "visit_crm_team_id",
            "visit_sale_order_template_id",
            "requests_sale_order_template_id",
            "visit_confirmation_policy",
            "installation_release_policy",
        ):
            field = settings._fields[field_name]
            self.assertTrue(field.related)
            self.assertFalse(field.store)

    def test_portal_configuration_is_company_specific(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create({"name": "Other Portal Company"})
        team_a = self.env["crm.team"].create(
            {"name": "Company A Visits", "company_id": company_a.id}
        )
        team_b = self.env["crm.team"].create(
            {"name": "Company B Visits", "company_id": company_b.id}
        )
        template_a = self.env["sale.order.template"].create(
            {
                "name": "Company A Survey",
                "service_type": "survey",
                "company_id": company_a.id,
            }
        )
        template_b = self.env["sale.order.template"].create(
            {
                "name": "Company B Survey",
                "service_type": "survey",
                "company_id": company_b.id,
            }
        )
        company_a.write(
            {
                "visit_crm_team_id": team_a.id,
                "visit_sale_order_template_id": template_a.id,
                "visit_confirmation_policy": "phone",
            }
        )
        company_b.write(
            {
                "visit_crm_team_id": team_b.id,
                "visit_sale_order_template_id": template_b.id,
                "visit_confirmation_policy": "payment",
            }
        )

        settings_a = self.env["res.config.settings"].with_company(company_a).create(
            {"company_id": company_a.id}
        )
        settings_b = self.env["res.config.settings"].with_company(company_b).create(
            {"company_id": company_b.id}
        )
        self.assertEqual(settings_a.visit_crm_team_id, team_a)
        self.assertEqual(settings_b.visit_crm_team_id, team_b)
        self.assertEqual(settings_a.visit_sale_order_template_id, template_a)
        self.assertEqual(settings_b.visit_sale_order_template_id, template_b)
        self.assertEqual(settings_a.visit_confirmation_policy, "phone")
        self.assertEqual(settings_b.visit_confirmation_policy, "payment")
