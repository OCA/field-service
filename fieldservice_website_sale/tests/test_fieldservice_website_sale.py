# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import pytz

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest

from ..controllers.main import FieldServiceController, PaymentPortal


class TestFieldServiceController(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].browse(1)
        cls.demo_user = cls.env.ref("base.demo_user0")
        cls.FieldServiceController = FieldServiceController()
        cls.PaymentPortalController = PaymentPortal()

        cls.test_person = cls.env.ref("fieldservice.test_person")
        cls.day_monday = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.day_wednesday = cls.env.ref("fieldservice_route.fsm_route_day_2")

        cls.blackout_day_1 = cls.env["fsm.blackout.day"].create(
            {"date": datetime(2025, 1, 25), "name": "Holiday 1"}
        )

        cls.fsm_route = cls.env["fsm.route"].create(
            {
                "name": "Test Route",
                "fsm_person_id": cls.test_person.id,
                "day_ids": [cls.day_monday.id, cls.day_wednesday.id],
                "max_order": 100,
            }
        )

        cls.partner_demo = cls.demo_user.partner_id
        fsm_wizard = cls.env["fsm.wizard"].create({})
        fsm_wizard.with_context(active_ids=[cls.partner_demo.id])
        fsm_wizard.action_convert_location(cls.partner_demo)

        cls.fsm_location = cls.env["fsm.location"].search(
            [("partner_id", "=", cls.partner_demo.id)]
        )

        cls.fsm_location.write({"fsm_route_id": cls.fsm_route.id})
        cls.payment_option_id = cls.env["payment.acquirer"].search([], limit=1).id

    def test_get_calendar_config(self):
        config = self.env["res.config.settings"].create(
            {
                "max_date_number": "3",
                "max_date_unit": "weeks",
            }
        )
        config.execute()

        with MockRequest(self.env, website=self.website.with_user(self.demo_user)):
            response = self.FieldServiceController.get_calendar_config()

        self.assertEqual(response["max_date_number"], "3")
        self.assertEqual(response["max_date_unit"], "weeks")

    def test_get_route_info(self):
        sale_order = self.env.ref("sale.portal_sale_order_2")

        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            response = self.FieldServiceController.get_route_info()

        self.assertEqual(response["route_assigned"], True)

        self.fsm_location.write({"fsm_route_id": False})

        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            response = self.FieldServiceController.get_route_info()

        self.assertEqual(response["route_assigned"], False)

    def test_get_enabled_days(self):
        sale_order = self.env.ref("sale.portal_sale_order_2")
        future_date = datetime.now() + timedelta(days=4)
        sale_order.write(
            {"fsm_location_id": self.fsm_location.id, "commitment_date": future_date}
        )

        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            response = self.FieldServiceController.get_enabled_days()

        # Assert that the correct enabled days are returned (Monday and Wednesday)
        self.assertEqual(response["enabled_days"], [1, 3])

        # Assert that the busy dates (commitment dates of confirmed sale orders)
        # are correctly returned
        busy_dates = [
            future_date.date().strftime("%Y-%m-%d"),
        ]
        self.assertEqual(response["busy_dates"], busy_dates)

        # Assert that route_assigned is not empty, meaning a route is assigned
        self.assertTrue(response["route_assigned"], "Route should be assigned.")

    def test_get_blackout_days(self):
        with MockRequest(self.env, website=self.website.with_user(self.demo_user)):
            response = self.FieldServiceController.get_blackout_days()

        disabled_dates = [
            self.blackout_day_1.date.strftime("%Y-%m-%d"),
        ]
        self.assertEqual(response["disabled_dates"], disabled_dates)

    def test_get_time_ranges(self):
        time_range_no_route = self.env["fsm.delivery.time.range"].create(
            {"start_time": 7, "end_time": 10, "route_id": False, "sequence": 1}
        )
        time_range_with_route = self.env["fsm.delivery.time.range"].create(
            {
                "start_time": 9,
                "end_time": 12,
                "route_id": self.fsm_route.id,
                "sequence": 2,
            }
        )

        sale_order = self.env.ref("sale.portal_sale_order_2")
        sale_order.write({"fsm_location_id": self.fsm_location.id})

        # Case 1: FSM location has a route assigned
        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            response = self.FieldServiceController.get_time_ranges()

        # Assert that both time ranges are included (one tied to the route and one global)
        expected_time_ranges = [
            {"id": time_range_no_route.id, "name": time_range_no_route.name},
            {"id": time_range_with_route.id, "name": time_range_with_route.name},
        ]
        self.assertEqual(response["time_ranges"], expected_time_ranges)

        # Case 2: FSM location has no route assigned
        self.fsm_location.write({"fsm_route_id": False})

        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            response = self.FieldServiceController.get_time_ranges()

        # Assert that only the global time range is included
        expected_time_ranges = [
            {"id": time_range_no_route.id, "name": time_range_no_route.name},
        ]
        self.assertEqual(response["time_ranges"], expected_time_ranges)

    def test_shop_payment_transaction(self):
        time_range = self.env["fsm.delivery.time.range"].create(
            {"start_time": 7, "end_time": 10, "route_id": False, "sequence": 1}
        )
        selected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        selected_time_range = time_range.id

        sale_order = self.env.ref("sale.portal_sale_order_2")
        sale_order.write({"fsm_location_id": self.fsm_location.id})

        # Case 1: Valid date and time range
        with MockRequest(
            sale_order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
            sale_order_id=sale_order.id,
        ):
            kwargs = {
                "access_token": "test_token",
                "order_id": sale_order.id,
                "selected_date": selected_date,
                "selected_time_range": selected_time_range,
                "amount": sale_order.amount_total,
                "payment_option_id": self.payment_option_id,
                "currency_id": sale_order.currency_id.id,
                "flow": "direct",
                "tokenization_requested": False,
                "landing_route": "/shop/payment/validate",
            }
            self.PaymentPortalController.shop_payment_transaction(**kwargs)

        # Assert that commitment dates are set correctly
        expected_start_datetime = self.PaymentPortalController._calculate_datetime(
            selected_date, time_range.start_time, pytz.UTC
        )
        expected_end_datetime = self.PaymentPortalController._calculate_datetime(
            selected_date, time_range.end_time, pytz.UTC
        )

        self.assertEqual(sale_order.commitment_date, expected_start_datetime)
        self.assertEqual(sale_order.commitment_date_end, expected_end_datetime)

        # Case 2: Missing selected_date
        with self.assertRaises(ValidationError):
            with MockRequest(
                sale_order.with_user(self.demo_user).env,
                website=self.website.with_user(self.demo_user),
                sale_order_id=sale_order.id,
            ):
                kwargs = {
                    "order_id": sale_order.id,
                    "selected_time_range": selected_time_range,
                }
                self.PaymentPortalController.shop_payment_transaction(**kwargs)

        # Case 3: Missing selected_time_range
        with self.assertRaises(ValidationError):
            with MockRequest(
                sale_order.with_user(self.demo_user).env,
                website=self.website.with_user(self.demo_user),
                sale_order_id=sale_order.id,
            ):
                kwargs = {
                    "order_id": sale_order.id,
                    "selected_date": selected_date,
                }
                self.PaymentPortalController.shop_payment_transaction(**kwargs)

    def test_calculate_datetime(self):
        selected_date = "2025-01-30"
        time_value = 9.5  # 9:30 AM
        user_timezone = pytz.timezone("Europe/Madrid")

        # Calculate datetime using helper method
        calculated_datetime = self.PaymentPortalController._calculate_datetime(
            selected_date, time_value, user_timezone
        )

        # Expected datetime in UTC
        localized_datetime = user_timezone.localize(
            datetime.strptime(selected_date, "%Y-%m-%d")
            + timedelta(hours=9, minutes=30)
        )
        expected_datetime = localized_datetime.astimezone(pytz.utc).replace(tzinfo=None)

        self.assertEqual(calculated_datetime, expected_datetime)
