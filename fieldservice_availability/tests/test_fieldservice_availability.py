# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFieldserviceAvailability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.time_range_model = cls.env["fsm.delivery.time.range"]
        cls.location_model = cls.env["fsm.location"]
        cls.route_model = cls.env["fsm.route"]
        cls.partner_model = cls.env["res.partner"]

        # Base partner required for fsm.location owner_id constraint
        cls.test_partner = cls.partner_model.create({"name": "Test Partner"})

        # Fixtures for hierarchy testing
        cls.global_range = cls.time_range_model.create(
            {"start_time": 8.0, "end_time": 18.0}
        )
        cls.route_range = cls.time_range_model.create(
            {"start_time": 8.0, "end_time": 16.0}
        )
        cls.test_route = cls.route_model.create(
            {
                "name": "Test Route",
                "delivery_time_range_ids": [(6, 0, [cls.route_range.id])],
            }
        )
        cls.loc_default_range = cls.time_range_model.create(
            {"start_time": 9.0, "end_time": 14.0}
        )
        cls.loc_summer_range = cls.time_range_model.create(
            {
                "start_time": 7.0,
                "end_time": 12.0,
                "month_start": "6",
                "day_start": 1,
                "month_end": "9",
                "day_end": 30,
            }
        )
        cls.test_location = cls.location_model.create(
            {
                "name": "Test Location",
                "owner_id": cls.test_partner.id,
                "fsm_route_id": cls.test_route.id,
            }
        )

    # -------------------------------------------------------------------------
    # Delivery Time Range Model Tests
    # -------------------------------------------------------------------------

    def test_01_create_valid_and_invalid_time_range(self):
        """Test time range creation, name computation, and time sequence validation."""
        time_range = self.time_range_model.create({"start_time": 8.0, "end_time": 12.0})
        self.assertEqual(time_range.name, "08:00 - 12:00")
        self.assertFalse(time_range.is_seasonal)

        with self.assertRaises(ValidationError):
            self.time_range_model.create({"start_time": 12.0, "end_time": 8.0})

    def test_02_seasonal_range_and_day_constraints(self):
        """Test recurring seasonal ranges and month day boundary constraints."""
        seasonal_range = self.time_range_model.create(
            {
                "start_time": 7.0,
                "end_time": 13.0,
                "month_start": "6",
                "day_start": 1,
                "month_end": "9",
                "day_end": 30,
            }
        )
        self.assertTrue(seasonal_range.is_seasonal)
        self.assertEqual(seasonal_range.name, "07:00 - 13:00 (1/6 - 30/9)")

        # Day 0 must raise ValidationError
        with self.assertRaises(ValidationError):
            self.time_range_model.create(
                {
                    "start_time": 8.0,
                    "end_time": 12.0,
                    "month_start": "6",
                    "day_start": 0,
                    "month_end": "6",
                    "day_end": 15,
                }
            )

        # April only has 30 days -> Day 31 must raise ValidationError
        with self.assertRaises(ValidationError):
            self.time_range_model.create(
                {
                    "start_time": 8.0,
                    "end_time": 12.0,
                    "month_start": "4",
                    "day_start": 31,
                    "month_end": "4",
                    "day_end": 30,
                }
            )

        # Leap year reference (2024) allows February 29
        leap_feb = self.time_range_model.create(
            {
                "start_time": 8.0,
                "end_time": 12.0,
                "month_start": "2",
                "day_start": 1,
                "month_end": "2",
                "day_end": 29,
            }
        )
        self.assertTrue(leap_feb.is_seasonal)

    def test_03_seasonal_active_date_evaluation(self):
        """Test evaluation of standard and cross-year recurring date ranges."""
        summer_range = self.time_range_model.create(
            {
                "start_time": 7.0,
                "end_time": 13.0,
                "month_start": "6",
                "day_start": 1,
                "month_end": "9",
                "day_end": 30,
            }
        )
        self.assertTrue(summer_range.is_active_on_date(date(2026, 7, 15)))
        self.assertFalse(summer_range.is_active_on_date(date(2026, 10, 1)))

        winter_range = self.time_range_model.create(
            {
                "start_time": 9.0,
                "end_time": 17.0,
                "month_start": "11",
                "day_start": 1,
                "month_end": "2",
                "day_end": 28,
            }
        )
        self.assertTrue(winter_range.is_active_on_date(date(2026, 12, 15)))
        self.assertTrue(winter_range.is_active_on_date(date(2027, 1, 15)))
        self.assertFalse(winter_range.is_active_on_date(date(2027, 6, 15)))

    # -------------------------------------------------------------------------
    # Location & Route Constraints and Hierarchy Resolution Tests
    # -------------------------------------------------------------------------

    def test_04_location_unique_default_schedule_constraint(self):
        """Ensure a location cannot have more than 1 non-seasonal default schedule."""
        default1 = self.time_range_model.create({"start_time": 8.0, "end_time": 12.0})
        default2 = self.time_range_model.create({"start_time": 13.0, "end_time": 17.0})

        with self.assertRaises(ValidationError):
            self.test_location.write(
                {"delivery_time_range_ids": [(6, 0, [default1.id, default2.id])]}
            )

    def test_05_route_unique_default_schedule_constraint(self):
        """Ensure a route cannot have more than 1 non-seasonal default schedule."""
        default1 = self.time_range_model.create({"start_time": 8.0, "end_time": 12.0})
        default2 = self.time_range_model.create({"start_time": 13.0, "end_time": 17.0})

        test_route = self.route_model.create({"name": "Constraint Route"})

        with self.assertRaises(ValidationError):
            test_route.write(
                {"delivery_time_range_ids": [(6, 0, [default1.id, default2.id])]}
            )

    def test_06_hierarchy_resolution(self):
        """Test fallback resolution order: Location Seasonal ->
        Location Default -> Route -> Global."""
        target_summer = date(2026, 7, 15)
        target_winter = date(2026, 12, 15)

        # 1. Global Fallback
        empty_loc = self.location_model.create(
            {
                "name": "Empty Location",
                "owner_id": self.test_partner.id,
            }
        )
        self.assertEqual(
            empty_loc.get_delivery_time_ranges(target_summer), self.global_range
        )

        # 2. Route Fallback
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(target_summer),
            self.route_range,
        )

        # Attach both Location Default AND Location Seasonal
        self.test_location.write(
            {
                "delivery_time_range_ids": [
                    (6, 0, [self.loc_default_range.id, self.loc_summer_range.id])
                ]
            }
        )

        # 3. Outside seasonal window (winter) -> Defaults to Location Default schedule
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(target_winter),
            self.loc_default_range,
        )

        # 4. Inside seasonal window (summer) -> Evaluates to Location Seasonal schedule
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(target_summer),
            self.loc_summer_range,
        )

    def test_07_incomplete_seasonal_dates_constraint(self):
        """Ensure partial seasonal definitions raise a ValidationError."""
        # Only start date provided -> must fail
        with self.assertRaises(ValidationError):
            self.time_range_model.create(
                {
                    "start_time": 8.0,
                    "end_time": 12.0,
                    "month_start": "6",
                    "day_start": 1,
                }
            )

        # Only end date provided -> must fail
        with self.assertRaises(ValidationError):
            self.time_range_model.create(
                {
                    "start_time": 8.0,
                    "end_time": 12.0,
                    "month_end": "9",
                    "day_end": 30,
                }
            )

    def test_08_additional_coverage_cases(self):
        """Test non-seasonal is_active_on_date, default target_date
        fallback, and datetime argument."""
        # 1. Calling is_active_on_date on a non-seasonal schedule returns True
        self.assertTrue(self.global_range.is_active_on_date(date(2026, 5, 10)))

        # 2. get_delivery_time_ranges without target_date parameter
        # (defaults to context_today)
        ranges_default_date = self.test_location.get_delivery_time_ranges()
        self.assertTrue(ranges_default_date)

        # 3. get_delivery_time_ranges passing a datetime object (converts to date)
        dt_target = datetime(2026, 7, 15, 10, 0, 0)
        ranges_from_datetime = self.test_location.get_delivery_time_ranges(
            target_date=dt_target
        )
        self.assertEqual(ranges_from_datetime, self.route_range)
