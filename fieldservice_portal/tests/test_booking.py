from datetime import timedelta
from unittest.mock import patch

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPortalBooking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Booking Customer"})
        location_partner = cls.env["res.partner"].create(
            {"name": "Booking Site", "parent_id": cls.partner.id}
        )
        cls.location = cls.env["fsm.location"].create(
            {"partner_id": location_partner.id, "owner_id": cls.partner.id}
        )
        cls.team = cls.env["fsm.team"].create(
            {"name": "Portal Booking Team", "company_id": cls.env.company.id}
        )
        cls.route = cls.env["fsm.route"].create(
            {
                "name": "Portal Survey Route",
                "route_type": "visit",
                "max_order": 5,
                "day_ids": [(6, 0, cls.env["fsm.route.day"].search([]).ids)],
            }
        )
        cls.dayroute = cls.env["fsm.route.dayroute"].create(
            {
                "route_id": cls.route.id,
                "team_id": cls.team.id,
                "date": fields.Date.today() + timedelta(days=1),
            }
        )
        cls.survey_type = cls.env["fsm.order.type"].search(
            [("service_type", "=", "survey")], limit=1
        ) or cls.env["fsm.order.type"].create(
            {"name": "Portal Survey", "service_type": "survey"}
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Portal Survey Service",
                "type": "service",
                "field_service_tracking": "sale",
                "list_price": 100.0,
            }
        )
        cls.line_service_product = cls.env["product.product"].create(
            {
                "name": "Portal Line Service",
                "type": "service",
                "field_service_tracking": "line",
            }
        )
        cls.survey_template = cls.env["sale.order.template"].create(
            {"name": "Portal Survey", "service_type": "survey"}
        )
        cls.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": cls.survey_template.id,
                "product_id": cls.service_product.id,
                "product_uom_id": cls.service_product.uom_id.id,
                "product_uom_qty": 1,
            }
        )
        cls.installation_template = cls.env["sale.order.template"].create(
            {"name": "Portal Installation", "service_type": "installation"}
        )

    def _create_sale(self, **values):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "fsm_location_id": self.location.id,
                "sale_order_template_id": self.survey_template.id,
                "portal_dayroute_id": self.dayroute.id,
                "portal_service_description": "Customer reported details",
                **values,
            }
        )

    def _set_dayroute_capacity(self, capacity):
        self.route.max_order = capacity
        self.dayroute._compute_order_count()

    def test_selected_dayroute_is_prepared_for_generated_fsm_orders(self):
        sale = self._create_sale()
        values = sale._prepare_fsm_values(so_id=sale.id)
        self.assertEqual(values["dayroute_id"], self.dayroute.id)
        self.assertEqual(
            fields.Datetime.to_datetime(values["request_early"]).date(),
            self.dayroute.date,
        )
        self.assertEqual(
            self.env["fsm.order.type"].browse(values["type"]).service_type,
            "survey",
        )
        self.assertEqual(values["team_id"], self.team.id)
        self.assertEqual(values["description"], "Customer reported details")

    def test_portal_quote_creates_no_fsm_order_before_confirmation(self):
        sale = self._create_sale()
        sale._onchange_sale_order_template_id()
        self.assertFalse(sale.fsm_order_ids)
        sale.action_confirm()
        self.assertEqual(len(sale.fsm_order_ids), 1)
        self.assertEqual(sale.fsm_order_ids.dayroute_id, self.dayroute)

    def test_phone_visit_waits_for_staff_confirmation(self):
        self.env.company.write(
            {
                "visit_confirmation_policy": "phone",
                "portal_confirmation_pay": True,
                "portal_confirmation_sign": True,
            }
        )
        sale = self._create_sale()
        sale._onchange_sale_order_template_id()

        self.assertFalse(sale._has_to_be_paid())
        self.assertFalse(sale._has_to_be_signed())
        self.assertFalse(sale._is_visit_released())

        sale.action_confirm()

        self.assertTrue(sale._is_visit_released())
        self.assertEqual(len(sale.fsm_order_ids), 1)

    def test_payment_visit_requires_full_payment_before_confirmation(self):
        self.env.company.visit_confirmation_policy = "payment"
        sale = self._create_sale()
        sale._onchange_sale_order_template_id()

        self.assertTrue(sale._has_to_be_paid())
        self.assertEqual(sale._get_prepayment_required_amount(), sale.amount_total)
        with self.assertRaisesRegex(UserError, "paid"):
            sale.action_confirm()

        self.assertEqual(sale.state, "draft")
        self.assertFalse(sale.fsm_order_ids)

    def test_paid_visit_confirms_and_generates_fsm(self):
        self.env.company.visit_confirmation_policy = "payment"
        sale = self._create_sale()
        sale._onchange_sale_order_template_id()

        with patch.object(type(sale), "_is_paid", autospec=True, return_value=True):
            sale.action_confirm()

        self.assertEqual(sale.state, "sale")
        self.assertEqual(len(sale.fsm_order_ids), 1)

    def test_survey_fsm_generation_rejects_unreleased_quotation(self):
        sale = self._create_sale()
        sale._onchange_sale_order_template_id()

        with self.assertRaisesRegex(ValidationError, "confirmed"):
            sale._field_service_generation()

        self.assertFalse(sale.fsm_order_ids)

    def test_installation_release_follows_company_policy(self):
        installation = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "fsm_location_id": self.location.id,
                "sale_order_template_id": self.installation_template.id,
                "state": "sale",
            }
        )

        self.env.company.installation_release_policy = "payment"
        self.assertFalse(installation._is_installation_released())
        with patch.object(
            type(installation), "_is_paid", autospec=True, return_value=True
        ):
            self.assertTrue(installation._is_installation_released())

        self.env.company.installation_release_policy = "approval"
        self.assertTrue(installation._is_installation_released())

    def test_all_line_generated_orders_receive_the_selected_appointment(self):
        line_values = {
            "product_id": self.line_service_product.id,
            "product_uom_id": self.line_service_product.uom_id.id,
            "product_uom_qty": 1,
        }
        sale = self._create_sale(
            order_line=[Command.create(line_values), Command.create(line_values)]
        )
        sale.action_confirm()
        self.assertEqual(len(sale.fsm_order_ids), 2)
        self.assertEqual(sale.fsm_order_ids.mapped("dayroute_id"), self.dayroute)

    def test_expired_dayroute_is_rejected(self):
        self.dayroute.date = fields.Date.today() - timedelta(days=1)
        with self.assertRaisesRegex(ValidationError, "no longer available"):
            self._create_sale()._validate_portal_dayroute("survey")

    def test_wrong_route_type_is_rejected(self):
        self.route.route_type = "maintenance"
        with self.assertRaisesRegex(ValidationError, "does not match"):
            self._create_sale()._validate_portal_dayroute("survey")

    def test_cross_company_dayroute_is_rejected(self):
        company = self.env["res.company"].create({"name": "Other Booking Company"})
        self.team.company_id = company
        with self.assertRaisesRegex(ValidationError, "not available for this company"):
            self._create_sale()._validate_portal_dayroute("survey")

    def test_capacity_accounts_for_all_generated_orders(self):
        self._set_dayroute_capacity(1)
        with self.assertRaisesRegex(ValidationError, "capacity"):
            self._create_sale()._validate_portal_dayroute("survey", needed_capacity=2)

    def test_active_draft_quotation_reserves_capacity(self):
        self._set_dayroute_capacity(1)
        reserved_sale = self._create_sale()
        confirming_sale = self._create_sale()

        with self.assertRaisesRegex(ValidationError, "capacity"):
            confirming_sale._validate_portal_dayroute("survey", lock=True)

        self.assertEqual(
            confirming_sale._portal_dayroute_reserved_capacity(
                self.dayroute, exclude_order=confirming_sale
            ),
            1,
        )
        self.assertEqual(reserved_sale.state, "draft")

    def test_cancelled_draft_quotation_releases_capacity(self):
        self._set_dayroute_capacity(1)
        reserved_sale = self._create_sale()
        confirming_sale = self._create_sale()

        reserved_sale.action_cancel()

        self.assertEqual(
            confirming_sale._portal_dayroute_reserved_capacity(
                self.dayroute, exclude_order=confirming_sale
            ),
            0,
        )
        self.assertEqual(
            confirming_sale._validate_portal_dayroute("survey", lock=True),
            self.dayroute,
        )

    def test_expired_draft_quotation_releases_capacity(self):
        self._set_dayroute_capacity(1)
        reserved_sale = self._create_sale(
            validity_date=fields.Date.context_today(self.env.user)
            - timedelta(days=1)
        )
        confirming_sale = self._create_sale()

        self.assertEqual(
            confirming_sale._portal_dayroute_reserved_capacity(
                self.dayroute, exclude_order=confirming_sale
            ),
            0,
        )
        self.assertEqual(
            confirming_sale._validate_portal_dayroute("survey", lock=True),
            self.dayroute,
        )
        self.assertEqual(reserved_sale.state, "draft")
