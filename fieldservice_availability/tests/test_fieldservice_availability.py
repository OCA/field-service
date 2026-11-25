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
        cls.route_day_model = cls.env["fsm.route.day"]

        cls.test_partner = cls.partner_model.create({"name": "Test Partner"})

        # Retrieve reference route days
        cls.day_mon = cls.route_day_model.search([("name", "=", "Monday")], limit=1)
        cls.day_wed = cls.route_day_model.search([("name", "=", "Wednesday")], limit=1)
        cls.day_fri = cls.route_day_model.search([("name", "=", "Friday")], limit=1)

        # 5. Global Fallback Range
        cls.global_range = cls.time_range_model.create(
            {"start_time": 7.0, "end_time": 15.0, "sequence": 1}
        )

        # Route Fixture with Default Schedule
        cls.test_route = cls.route_model.create(
            {
                "name": "Test Route",
                "has_default_schedule": True,
                "default_start_time": 8.0,
                "default_end_time": 16.0,
                "day_ids": [(6, 0, [cls.day_mon.id, cls.day_wed.id])],
            }
        )

        # Location Fixture
        cls.test_location = cls.location_model.create(
            {
                "name": "Test Location",
                "owner_id": cls.test_partner.id,
                "fsm_route_id": cls.test_route.id,
            }
        )

    # -------------------------------------------------------------------------
    # 1. Global Delivery Time Range Model Tests
    # -------------------------------------------------------------------------

    def test_01_global_time_range_creation_and_constraints(self):
        """Test global time range name computation and strict hour constraints."""
        time_range = self.time_range_model.create({"start_time": 8.0, "end_time": 12.0})
        self.assertEqual(time_range.name, "08:00 - 12:00")

        # Start time >= End time
        with self.assertRaises(ValidationError):
            self.time_range_model.create({"start_time": 12.0, "end_time": 8.0})

        # Hour >= 24.0
        with self.assertRaises(ValidationError):
            self.time_range_model.create({"start_time": 8.0, "end_time": 24.0})

        # Negative hour
        with self.assertRaises(ValidationError):
            self.time_range_model.create({"start_time": -1.0, "end_time": 12.0})

    # -------------------------------------------------------------------------
    # 2. Schedule Mixin Constraints Tests
    # -------------------------------------------------------------------------

    def test_02_default_and_seasonal_time_constraints(self):
        """Test time range validation on location default and seasonal hours."""
        # Default start >= end
        with self.assertRaises(ValidationError):
            self.test_location.create(
                {
                    "name": "Invalid Location",
                    "owner_id": self.test_partner.id,
                    "has_default_schedule": True,
                    "default_start_time": 14.0,
                    "default_end_time": 10.0,
                }
            )

        # Seasonal start >= end
        with self.assertRaises(ValidationError):
            self.test_location.create(
                {
                    "name": "Invalid Seasonal Location",
                    "owner_id": self.test_partner.id,
                    "has_seasonal_schedule": True,
                    "seasonal_month_start": "6",
                    "seasonal_day_start": 1,
                    "seasonal_month_end": "8",
                    "seasonal_day_end": 31,
                    "seasonal_start_time": 18.0,
                    "seasonal_end_time": 12.0,
                }
            )

    def test_03_seasonal_date_validation_and_leap_year(self):
        """Test month/day boundary constraints and incomplete
        seasonal date definitions."""
        with self.assertRaises(ValidationError):
            self.location_model.create(
                {
                    "name": "Incomplete Season",
                    "owner_id": self.test_partner.id,
                    "has_seasonal_schedule": True,
                    "seasonal_month_start": "6",
                    "seasonal_day_start": 1,
                }
            )

        with self.assertRaises(ValidationError):
            self.location_model.create(
                {
                    "name": "Invalid April Day",
                    "owner_id": self.test_partner.id,
                    "has_seasonal_schedule": True,
                    "seasonal_month_start": "4",
                    "seasonal_day_start": 31,
                    "seasonal_month_end": "5",
                    "seasonal_day_end": 15,
                    "seasonal_start_time": 8.0,
                    "seasonal_end_time": 12.0,
                }
            )

        leap_loc = self.location_model.create(
            {
                "name": "Leap Feb Location",
                "owner_id": self.test_partner.id,
                "has_seasonal_schedule": True,
                "seasonal_month_start": "2",
                "seasonal_day_start": 1,
                "seasonal_month_end": "2",
                "seasonal_day_end": 29,
                "seasonal_start_time": 8.0,
                "seasonal_end_time": 12.0,
            }
        )
        self.assertTrue(leap_loc.has_seasonal_schedule)

    # -------------------------------------------------------------------------
    # 3. Hierarchy and Schedule Resolution Tests
    # -------------------------------------------------------------------------

    def test_04_default_schedule_resolution(self):
        """Test location default schedule resolution vs route fallback."""
        monday = date(2026, 7, 13)

        # 1. Location has no default schedule -> Resolves to
        # Route Default (08:00 - 16:00)
        hours = self.test_location.get_delivery_time_ranges(monday)
        self.assertEqual(hours, (8.0, 16.0))

        # 2. Enable location default schedule -> Resolves to Location
        # Default (10:00 - 14:00)
        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 10.0,
                "default_end_time": 14.0,
            }
        )
        hours = self.test_location.get_delivery_time_ranges(monday)
        self.assertEqual(hours, (10.0, 14.0))

    def test_05_seasonal_schedule_resolution(self):
        """Test active seasonal schedule window vs winter fallback
        to default schedule."""
        summer_day = date(2026, 7, 15)
        winter_day = date(2026, 12, 16)

        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 10.0,
                "default_end_time": 14.0,
                "has_seasonal_schedule": True,
                "seasonal_month_start": "6",
                "seasonal_day_start": 1,
                "seasonal_month_end": "8",
                "seasonal_day_end": 31,
                "seasonal_start_time": 7.0,
                "seasonal_end_time": 11.0,
            }
        )

        hours_summer = self.test_location.get_delivery_time_ranges(summer_day)
        self.assertEqual(hours_summer, (7.0, 11.0))

        hours_winter = self.test_location.get_delivery_time_ranges(winter_day)
        self.assertEqual(hours_winter, (10.0, 14.0))

    def test_06_day_specific_schedule_resolution(self):
        """Test day-of-week grid lines override general default/seasonal schedules."""
        monday = date(2026, 7, 13)
        wednesday = date(2026, 7, 15)

        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 10.0,
                "default_end_time": 14.0,
                "has_day_schedule": True,
                "default_schedule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "day_of_week": "2",
                            "start_time": 11.0,
                            "end_time": 13.0,
                            "is_seasonal": False,
                        },
                    )
                ],
            }
        )

        hours_wed = self.test_location.get_delivery_time_ranges(wednesday)
        self.assertEqual(hours_wed, (11.0, 13.0))

        hours_mon = self.test_location.get_delivery_time_ranges(monday)
        self.assertEqual(hours_mon, (10.0, 14.0))

    def test_07_full_hierarchy_resolution(self):
        """Test full 5-tier cascade: Loc Seasonal -> Loc Default ->
        Route Seasonal -> Route Default -> Global."""
        summer_day = date(2026, 7, 15)

        empty_loc = self.location_model.create(
            {"name": "Empty Loc", "owner_id": self.test_partner.id}
        )

        # Tier 5: Global Fallback (07:00 - 15:00)
        self.assertEqual(empty_loc.get_delivery_time_ranges(summer_day), (7.0, 15.0))

        # Tier 4: Route Default (08:00 - 16:00)
        empty_loc.fsm_route_id = self.test_route
        self.assertEqual(empty_loc.get_delivery_time_ranges(summer_day), (8.0, 16.0))

        # Tier 3: Route Seasonal (06:00 - 12:00)
        self.test_route.write(
            {
                "has_seasonal_schedule": True,
                "seasonal_month_start": "6",
                "seasonal_day_start": 1,
                "seasonal_month_end": "8",
                "seasonal_day_end": 31,
                "seasonal_start_time": 6.0,
                "seasonal_end_time": 12.0,
            }
        )
        self.assertEqual(empty_loc.get_delivery_time_ranges(summer_day), (6.0, 12.0))

        # Tier 2: Location Default (09:00 - 17:00)
        empty_loc.write(
            {
                "has_default_schedule": True,
                "default_start_time": 9.0,
                "default_end_time": 17.0,
            }
        )
        self.assertEqual(empty_loc.get_delivery_time_ranges(summer_day), (9.0, 17.0))

        # Tier 1: Location Seasonal (05:00 - 10:00)
        empty_loc.write(
            {
                "has_seasonal_schedule": True,
                "seasonal_month_start": "6",
                "seasonal_day_start": 1,
                "seasonal_month_end": "8",
                "seasonal_day_end": 31,
                "seasonal_start_time": 5.0,
                "seasonal_end_time": 10.0,
            }
        )
        self.assertEqual(empty_loc.get_delivery_time_ranges(summer_day), (5.0, 10.0))

    # -------------------------------------------------------------------------
    # 4. Operational Days and Line Constraints Tests
    # -------------------------------------------------------------------------

    def test_08_day_of_week_allowed_constraint(self):
        """Ensure schedule lines cannot be added for days not allowed
        on location/route."""
        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 10.0,
                "default_end_time": 14.0,
                "has_day_schedule": True,
            }
        )

        with self.assertRaises(ValidationError):
            self.env["fsm.location.delivery.schedule.line"].create(
                {
                    "location_id": self.test_location.id,
                    "day_of_week": "4",
                    "start_time": 10.0,
                    "end_time": 12.0,
                    "is_seasonal": False,
                }
            )

        self.test_location.day_ids = [(4, self.day_fri.id)]
        line = self.env["fsm.location.delivery.schedule.line"].create(
            {
                "location_id": self.test_location.id,
                "day_of_week": "4",
                "start_time": 10.0,
                "end_time": 12.0,
                "is_seasonal": False,
            }
        )
        self.assertTrue(line)

    def test_09_allowed_route_days_resolution(self):
        """Test allowed route days resolution priority: Location ->
        Route -> Company -> Active search."""
        empty_loc = self.location_model.create(
            {"name": "No Route Loc", "owner_id": self.test_partner.id}
        )

        # Ensure company setting is empty for the baseline test
        self.env.company.fsm_default_route_day_ids = False

        # 1. Neither location, route, nor company set -> Returns all active route days
        all_active_days = self.route_day_model.search([])
        self.assertEqual(
            set(empty_loc.get_allowed_route_days().ids),
            set(all_active_days.ids),
        )

        # 2. Company setting configured -> Overrides all active days fallback
        self.env.company.fsm_default_route_day_ids = [
            (6, 0, [self.day_mon.id, self.day_wed.id])
        ]
        self.assertEqual(
            set(empty_loc.get_allowed_route_days().ids),
            {self.day_mon.id, self.day_wed.id},
        )

        # 3. Route set -> Inherits route days (overrides company)
        self.test_route.day_ids = [(6, 0, [self.day_mon.id])]
        empty_loc.fsm_route_id = self.test_route
        self.assertEqual(
            set(empty_loc.get_allowed_route_days().ids),
            {self.day_mon.id},
        )

        # 4. Location day_ids set -> Overrides route days (and company)
        empty_loc.day_ids = [(6, 0, [self.day_fri.id])]
        self.assertEqual(
            set(empty_loc.get_allowed_route_days().ids),
            {self.day_fri.id},
        )

    def test_10_target_date_parameter_formats(self):
        """Test get_delivery_time_ranges parameter acceptance (date,
        datetime, ISO string, None)."""
        d_target = date(2026, 7, 15)
        dt_target = datetime(2026, 7, 15, 10, 30, 0)
        str_target = "2026-07-15"

        # 1. date object
        self.assertTrue(
            self.test_location.get_delivery_time_ranges(target_date=d_target)
        )
        # 2. datetime object
        self.assertTrue(
            self.test_location.get_delivery_time_ranges(target_date=dt_target)
        )
        # 3. ISO date string
        self.assertTrue(
            self.test_location.get_delivery_time_ranges(target_date=str_target)
        )
        # 4. None (defaults to today)
        self.assertTrue(self.test_location.get_delivery_time_ranges())

    # -------------------------------------------------------------------------
    # 5. Additional Edge Cases & Secondary Models
    # -------------------------------------------------------------------------

    def test_11_cross_year_seasonal_schedule_resolution(self):
        """Test seasonal schedules that wrap across the calendar year boundary."""
        december_day = date(2026, 12, 15)
        january_day = date(2027, 1, 15)
        july_day = date(2027, 7, 15)

        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 8.0,
                "default_end_time": 16.0,
                "has_seasonal_schedule": True,
                "seasonal_month_start": "11",
                "seasonal_day_start": 1,
                "seasonal_month_end": "2",
                "seasonal_day_end": 28,
                "seasonal_start_time": 9.0,
                "seasonal_end_time": 13.0,
            }
        )

        self.assertEqual(
            self.test_location.get_delivery_time_ranges(december_day), (9.0, 13.0)
        )
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(january_day), (9.0, 13.0)
        )
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(july_day), (8.0, 16.0)
        )

    def test_12_seasonal_day_specific_schedule_resolution(self):
        """Test day-of-week grid lines for seasonal schedules."""
        wednesday = date(2026, 7, 15)
        friday = date(2026, 7, 17)

        # Explicitly allow both Wednesday and Friday on the location
        self.test_location.day_ids = [(6, 0, [self.day_wed.id, self.day_fri.id])]
        self.test_location.write(
            {
                "has_seasonal_schedule": True,
                "seasonal_month_start": "6",
                "seasonal_day_start": 1,
                "seasonal_month_end": "8",
                "seasonal_day_end": 31,
                "seasonal_start_time": 7.0,
                "seasonal_end_time": 15.0,
                "has_seasonal_day_schedule": True,
                "seasonal_schedule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "day_of_week": "2",
                            "start_time": 8.0,
                            "end_time": 12.0,
                            "is_seasonal": True,
                        },
                    )
                ],
            }
        )

        self.assertEqual(
            self.test_location.get_delivery_time_ranges(wednesday), (8.0, 12.0)
        )
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(friday), (7.0, 15.0)
        )

    def test_13_empty_global_time_ranges_hard_fallback(self):
        """Test absolute python fallback (7.0, 15.0) when no global ranges exist."""
        empty_loc = self.location_model.create(
            {"name": "No Schedule Loc", "owner_id": self.test_partner.id}
        )
        self.time_range_model.search([]).unlink()
        self.assertEqual(
            empty_loc.get_delivery_time_ranges(date(2026, 7, 15)), (7.0, 15.0)
        )

    def test_14_combined_default_and_seasonal_day_schedules(self):
        """Test coexistence of both default and seasonal day-specific schedule
        grids on the same location."""
        summer_wednesday = date(2026, 7, 15)
        winter_wednesday = date(2026, 12, 16)

        self.test_location.day_ids = [(6, 0, [self.day_wed.id])]
        self.test_location.write(
            {
                # Default Schedule + Day Grid (Wed: 09:00 - 13:00)
                "has_default_schedule": True,
                "default_start_time": 10.0,
                "default_end_time": 16.0,
                "has_day_schedule": True,
                "default_schedule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "day_of_week": "2",
                            "start_time": 9.0,
                            "end_time": 13.0,
                            "is_seasonal": False,
                        },
                    )
                ],
                # Seasonal Schedule + Day Grid (Wed: 06:00 - 10:00)
                "has_seasonal_schedule": True,
                "seasonal_month_start": "6",
                "seasonal_day_start": 1,
                "seasonal_month_end": "8",
                "seasonal_day_end": 31,
                "seasonal_start_time": 7.0,
                "seasonal_end_time": 11.0,
                "has_seasonal_day_schedule": True,
                "seasonal_schedule_line_ids": [
                    (
                        0,
                        0,
                        {
                            "day_of_week": "2",
                            "start_time": 6.0,
                            "end_time": 10.0,
                            "is_seasonal": True,
                        },
                    )
                ],
            }
        )

        # 1. Summer Wednesday -> Resolves to Seasonal Day Line (06:00 - 10:00)
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(summer_wednesday),
            (6.0, 10.0),
        )

        # 2. Winter Wednesday -> Resolves to Default Day Line (09:00 - 13:00)
        self.assertEqual(
            self.test_location.get_delivery_time_ranges(winter_wednesday),
            (9.0, 13.0),
        )
