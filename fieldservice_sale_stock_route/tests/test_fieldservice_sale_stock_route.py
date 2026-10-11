# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import pytz
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFieldServiceSaleStockRoute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.Picking = cls.env["stock.picking"]
        cls.FSMOrder = cls.env["fsm.order"]
        cls.TimeRange = cls.env["fsm.delivery.time.range"]

        cls.product_10 = cls.env.ref("product.product_product_10")
        cls.product_10.write({"field_service_tracking": "sale"})

        cls.fsm_day_monday = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.fsm_day_thursday = cls.env.ref("fieldservice_route.fsm_route_day_3")

        cls.test_partner = cls.env.ref("fieldservice.test_loc_partner")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.test_person = cls.env.ref("fieldservice.test_person")

        cls.test_route = cls.env["fsm.route"].create(
            {
                "name": "Test Route",
                "fsm_person_id": cls.test_person.id,
                "day_ids": [(6, 0, [cls.fsm_day_monday.id, cls.fsm_day_thursday.id])],
                "max_order": 1000,
            }
        )
        cls.test_location.write({"fsm_route_id": cls.test_route.id})

        cls.sale_order = cls.SaleOrder.create(
            {
                "partner_id": cls.test_partner.id,
                "fsm_location_id": cls.test_location.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_10.id, "product_uom_qty": 1})
                ],
                "state": "draft",
            }
        )

    def _create_sale_order(self, location=None, commitment_date=None):
        """Helper to create sale orders in draft state for test scenarios."""
        vals = {
            "partner_id": self.test_partner.id,
            "fsm_location_id": (location or self.test_location).id,
            "order_line": [
                (0, 0, {"product_id": self.product_10.id, "product_uom_qty": 1})
            ],
            "state": "draft",
        }
        if commitment_date:
            vals["commitment_date"] = commitment_date
        return self.SaleOrder.create(vals)

    def _assert_order_local_hours(
        self,
        order,
        expected_start_hour,
        expected_end_hour,
        expected_start_date=None,
        expected_end_date=None,
    ):
        """Helper to assert local start and end dates/hours on SO and FSM order."""
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        local_tz = pytz.timezone(tz_name)
        start_local = pytz.utc.localize(order.commitment_date).astimezone(local_tz)
        end_local = pytz.utc.localize(order.commitment_date_end).astimezone(local_tz)

        self.assertEqual(start_local.hour, expected_start_hour)
        self.assertEqual(end_local.hour, expected_end_hour)

        if expected_start_date:
            self.assertEqual(start_local.date(), expected_start_date)
        if expected_end_date:
            self.assertEqual(end_local.date(), expected_end_date)

        # Verify generated FSM order receives the exact dates
        fsm_order = self.FSMOrder.search([("sale_id", "=", order.id)], limit=1)
        if fsm_order:
            self.assertEqual(fsm_order.scheduled_date_start, order.commitment_date)
            self.assertEqual(fsm_order.scheduled_date_end, order.commitment_date_end)

    @freeze_time("2025-05-15")
    def test_01_commitment_dates_on_confirmation_default(self):
        """
        Test that commitment_date and commitment_date_end are automatically
        assigned to the next available route day when left empty upon SO confirmation.
        """
        tomorrow = fields.Datetime.now() + timedelta(days=1)
        next_route_day = self.sale_order._get_next_route_day(from_date=tomorrow)
        expected_start, expected_end = self.sale_order._apply_time_range_to_dates(
            next_route_day
        )
        self.sale_order.action_confirm()

        self.assertTrue(
            self.sale_order.commitment_date,
            "Commitment date should be set after confirmation.",
        )
        self.assertEqual(
            self.sale_order.commitment_date,
            expected_start,
            "Commitment date should match next route day start time.",
        )
        self.assertEqual(
            self.sale_order.commitment_date_end,
            expected_end,
            "Commitment date end should match next route day end time.",
        )

    @freeze_time("2025-05-15")
    def test_02_commitment_dates_on_confirmation_manual_date(self):
        """
        Test that user-selected manual delivery date is respected on SO confirm,
        while start and end hours are standardized using the schedule hierarchy.
        """
        manual_date = datetime(2025, 5, 19, 14, 30, 0)  # Monday
        so = self._create_sale_order(commitment_date=manual_date)
        so.action_confirm()

        self.assertEqual(so.commitment_date.date(), manual_date.date())
        self.assertTrue(so.commitment_date_end)
        self._assert_order_local_hours(
            so,
            expected_start_hour=7,
            expected_end_hour=15,
            expected_start_date=manual_date.date(),
        )

    def test_03_route_validation_and_force_schedule(self):
        """Test flexible confirmation, route day restrictions, and
        Force Schedule override."""
        # 1. Flexible confirmation allows confirming even without route or driver
        no_route_so = self._create_sale_order()
        no_route_so.fsm_location_id.write({"fsm_route_id": False})
        no_route_so.action_confirm()
        self.assertEqual(no_route_so.state, "sale")

        # 2. ValidationError raised if commitment_date is set to an unallowed route day
        invalid_so = self._create_sale_order()
        invalid_so.fsm_location_id.write({"fsm_route_id": self.test_route.id})
        self.test_route.write({"force_schedule": False})

        # Set an unallowed day (Wednesday is not in Mon/Thu route)
        invalid_so.commitment_date = datetime(2025, 5, 14, 10, 0, 0)
        with self.assertRaises(ValidationError):
            invalid_so.action_confirm()

        # 3. Enable force_schedule on route allows overriding the day restriction
        self.test_route.write({"force_schedule": True})
        invalid_so.action_confirm()
        self.assertEqual(invalid_so.state, "sale")

    @freeze_time("2025-05-15")
    def test_04_write_commitment_date_syncs_related_records(self):
        """Test writing new commitment_date on SO updates pickings and FSM orders."""
        self.sale_order.action_confirm()
        related_picking = self.sale_order.picking_ids.filtered(
            lambda r: r.state not in ["done", "cancel"]
        )
        related_fsm_order = self.FSMOrder.search(
            [("sale_id", "=", self.sale_order.id)], limit=1
        )

        next_route_day = self.sale_order._get_next_route_day()
        self.sale_order.write({"commitment_date": next_route_day})

        self.assertEqual(
            related_picking.scheduled_date,
            self.sale_order.commitment_date,
            "Picking scheduled_date should sync with SO commitment_date.",
        )
        self.assertEqual(
            related_fsm_order.scheduled_date_start,
            self.sale_order.commitment_date,
            "FSM order start date should sync with SO commitment_date.",
        )
        self.assertEqual(
            related_fsm_order.scheduled_date_end,
            self.sale_order.commitment_date_end,
            "FSM order end date should sync with SO commitment_date_end.",
        )

    @freeze_time("2025-05-15")
    def test_05_fsm_order_write_same_day_vs_calendar_shift(self):
        """Test FSM order write behavior: calendar day shift re-evaluates
        schedule, same day edit preserves hours."""
        self.sale_order.action_confirm()
        fsm_order = self.FSMOrder.search(
            [("sale_id", "=", self.sale_order.id)], limit=1
        )

        # 1. Same-day hour edit -> Preserves dispatcher's custom time slot
        same_day_new_time = datetime(2025, 5, 19, 11, 30, 0)
        fsm_order.write({"scheduled_date_start": same_day_new_time})

        self.assertEqual(fsm_order.scheduled_date_start, same_day_new_time)
        self.assertEqual(self.sale_order.commitment_date, same_day_new_time)

        # 2. Calendar day shift (Mon -> Thu) -> Re-evaluates hierarchy default hours
        different_day = datetime(2025, 5, 22, 14, 0, 0)
        fsm_order.write({"scheduled_date_start": different_day})

        expected_start, expected_end = self.sale_order._apply_time_range_to_dates(
            different_day
        )
        self.assertEqual(fsm_order.scheduled_date_start, expected_start)
        self.assertEqual(fsm_order.scheduled_date_end, expected_end)
        self.assertEqual(self.sale_order.commitment_date, expected_start)

    @freeze_time("2025-05-15")
    def test_06_postpone_delivery_workflow(self):
        """Test Postpone Delivery header button action and visibility."""
        self.sale_order.action_confirm()
        fsm_order = self.FSMOrder.search(
            [("sale_id", "=", self.sale_order.id)], limit=1
        )

        fsm_order._compute_postpone_button_visibility()
        self.assertTrue(fsm_order.show_postpone_button)

        next_route_day = self.sale_order._get_next_route_day(
            from_date=self.sale_order.commitment_date + timedelta(days=1)
        )
        fsm_order.action_postpone_delivery()

        expected_start, expected_end = self.sale_order._apply_time_range_to_dates(
            next_route_day
        )
        self.assertEqual(fsm_order.scheduled_date_start, expected_start)
        self.assertEqual(fsm_order.scheduled_date_end, expected_end)
        self.assertEqual(self.sale_order.commitment_date, expected_start)

        # Verify postpone message posted in FSM order chatter
        messages = fsm_order.message_ids.filtered(
            lambda m: "Delivery postponed" in m.body
        )
        self.assertTrue(messages)

    @freeze_time("2025-05-15")
    def test_07_clear_dates_behavior(self):
        """Test setting commitment_date or scheduled_date_start to blank (False)."""
        self.sale_order.action_confirm()
        fsm_order = self.FSMOrder.search(
            [("sale_id", "=", self.sale_order.id)], limit=1
        )
        related_picking = self.sale_order.picking_ids.filtered(
            lambda r: r.state not in ["done", "cancel"]
        )

        # 1. Clear commitment_date on Sale Order
        self.sale_order.write({"commitment_date": False})

        self.assertFalse(self.sale_order.commitment_date)
        self.assertFalse(self.sale_order.commitment_date_end)
        self.assertFalse(fsm_order.scheduled_date_start)
        self.assertFalse(fsm_order.scheduled_date_end)
        self.assertEqual(fsm_order.scheduled_duration, 0.0)

        # Stock picking scheduled_date safely falls back to expected_date (no TypeError)
        self.assertTrue(related_picking.scheduled_date)

        # 2. Clear scheduled_date_start on FSM Order
        fsm_order.write({"scheduled_date_start": datetime(2025, 5, 19, 8, 0)})
        self.assertTrue(self.sale_order.commitment_date)

        fsm_order.write({"scheduled_date_start": False})
        self.assertFalse(self.sale_order.commitment_date)
        self.assertFalse(fsm_order.scheduled_date_start)
        self.assertEqual(fsm_order.scheduled_duration, 0.0)

    @freeze_time("2025-05-15")
    def test_08_hierarchy_level1_location_seasonal(self):
        """Level 1: Location Seasonal Schedule overrides lower level
        schedules on SO confirm."""
        self.test_location.write(
            {
                "has_seasonal_schedule": True,
                "seasonal_month_start": "5",
                "seasonal_day_start": 1,
                "seasonal_month_end": "5",
                "seasonal_day_end": 31,
                "seasonal_start_time": 7.0,
                "seasonal_end_time": 11.0,
                "has_default_schedule": True,
                "default_start_time": 8.0,
                "default_end_time": 14.0,
            }
        )
        self.test_route.write(
            {
                "has_default_schedule": True,
                "default_start_time": 9.0,
                "default_end_time": 17.0,
            }
        )

        so = self._create_sale_order()
        so.action_confirm()
        self._assert_order_local_hours(so, 7, 11)

    @freeze_time("2025-05-15")
    def test_09_hierarchy_level2_location_default(self):
        """Level 2: Location Default Schedule applies on SO confirm when
        no seasonal range matches."""
        self.test_location.write(
            {
                "has_default_schedule": True,
                "default_start_time": 8.0,
                "default_end_time": 14.0,
            }
        )
        self.test_route.write(
            {
                "has_default_schedule": True,
                "default_start_time": 9.0,
                "default_end_time": 17.0,
            }
        )

        so = self._create_sale_order()
        so.action_confirm()
        self._assert_order_local_hours(so, 8, 14)

    @freeze_time("2025-05-15")
    def test_10_hierarchy_level3_route_seasonal(self):
        """Level 3: Route Seasonal Schedule applies on SO confirm when
        Location has no time ranges."""
        self.test_route.write(
            {
                "has_seasonal_schedule": True,
                "seasonal_month_start": "5",
                "seasonal_day_start": 1,
                "seasonal_month_end": "5",
                "seasonal_day_end": 31,
                "seasonal_start_time": 6.0,
                "seasonal_end_time": 10.0,
                "has_default_schedule": True,
                "default_start_time": 9.0,
                "default_end_time": 17.0,
            }
        )

        so = self._create_sale_order()
        so.action_confirm()
        self._assert_order_local_hours(so, 6, 10)

    @freeze_time("2025-05-15")
    def test_11_hierarchy_level4_route_default(self):
        """Level 4: Route Default Schedule applies on SO confirm when
        Location has no schedule & Route has no seasonal match."""
        self.test_route.write(
            {
                "has_default_schedule": True,
                "default_start_time": 9.0,
                "default_end_time": 17.0,
            }
        )

        so = self._create_sale_order()
        so.action_confirm()
        self._assert_order_local_hours(so, 9, 17)

    @freeze_time("2025-05-15")
    def test_12_hierarchy_level5_global_fallback(self):
        """Level 5: Global Fallback Schedule applies on SO confirm when
        neither Location nor Route specify schedules."""
        self.TimeRange.create({"start_time": 10.0, "end_time": 12.0, "sequence": 1})

        so = self._create_sale_order()
        so.action_confirm()
        self._assert_order_local_hours(so, 10, 12)

    @freeze_time("2025-05-15")
    def test_13_fsm_order_duration_edit_syncs_commitment_date_end(self):
        """Test editing scheduled_duration on FSM order recalculates
        commitment_date_end on SO."""
        self.sale_order.action_confirm()
        fsm_order = self.FSMOrder.search(
            [("sale_id", "=", self.sale_order.id)], limit=1
        )
        fsm_order.write({"scheduled_duration": fsm_order.scheduled_duration + 2.0})
        expected_end = fsm_order.scheduled_date_start + timedelta(
            hours=fsm_order.scheduled_duration
        )
        self.assertEqual(fsm_order.scheduled_date_end, expected_end)
        self.assertEqual(self.sale_order.commitment_date_end, expected_end)
