# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFieldServiceSaleStockRoute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.Picking = cls.env["stock.picking"]
        cls.FSMOrder = cls.env["fsm.order"]

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

    @freeze_time("2025-05-15")
    def test_commitment_dates_on_confirmation(self):
        """
        Test that commitment_date and commitment_date_end are correctly
        computed when the sale order is confirmed.
        """
        next_route_day = self.sale_order._get_next_route_day()
        self.sale_order._action_confirm()

        self.assertTrue(
            self.sale_order.commitment_date,
            "Commitment date should be set after confirmation.",
        )

        self.assertEqual(
            self.sale_order.commitment_date_end,
            next_route_day,
            "Commitment date end should match the next route day after confirmation.",
        )

        self.assertEqual(
            self.sale_order.commitment_date_end,
            self.sale_order.commitment_date,
            "Commitment date end should match commitment date after confirmation.",
        )

    @freeze_time("2025-05-15")
    def test_commitment_date_end_before_commitment_date(self):
        """
        Test that commitment_date_end is set to commitment_date if
        commitment_date_end is set before commitment_date.
        """
        self.sale_order.commitment_date = datetime.now()
        self.sale_order.commitment_date_end = (
            self.sale_order.commitment_date - timedelta(days=1)
        )
        self.assertEqual(
            self.sale_order.commitment_date,
            self.sale_order.commitment_date_end,
            "Commitment date should match commitment date end.",
        )

    def test_validation_on_confirmation(self):
        """Test that the FSM route is validated when the sale order is confirmed."""
        self.sale_order.fsm_location_id.write({"fsm_route_id": False})
        with self.assertRaises(ValidationError):
            self.sale_order._action_confirm()

        self.sale_order.fsm_location_id.write({"fsm_route_id": self.test_route.id})
        self.test_route.write({"fsm_person_id": False})
        with self.assertRaises(ValidationError):
            self.sale_order._action_confirm()

        self.test_route.write({"fsm_person_id": self.test_person.id})
        self.test_route.write({"day_ids": [(5, 0, 0)]})
        with self.assertRaises(ValidationError):
            self.sale_order._action_confirm()

        self.test_route.write(
            {"day_ids": [(6, 0, [self.fsm_day_monday.id, self.fsm_day_thursday.id])]}
        )
        # Test that a ValidationError is raised if the commitment_date
        # is set to a day not in the route days.
        invalid_commitment_date = self.sale_order._get_next_route_day() - timedelta(
            days=1
        )
        self.sale_order.commitment_date = invalid_commitment_date
        with self.assertRaises(ValidationError):
            self.sale_order._action_confirm()

    @freeze_time("2025-05-15")
    def test_write_commitment_dates_to_related_records(self):
        """Test that commitment_date is written to related pickings and FSM orders."""
        next_route_day = self.sale_order._get_next_route_day()
        self.sale_order.action_confirm()
        related_picking = self.sale_order.picking_ids.filtered(
            lambda r: r.state not in ["done", "cancel"]
        )
        related_fsm_order = self.env["fsm.order"].search(
            [
                ("sale_id", "=", self.sale_order.id),
                ("sale_line_id", "=", False),
                ("is_closed", "=", False),
            ]
        )

        self.assertEqual(
            self.sale_order.commitment_date,
            related_picking.scheduled_date,
            "Scheduled date on pickings should match commitment date.",
        )

        self.assertEqual(
            self.sale_order.commitment_date,
            related_fsm_order.scheduled_date_start,
            "Scheduled start date on FSM orders should match commitment date.",
        )

        self.assertEqual(
            self.sale_order.commitment_date,
            related_fsm_order.scheduled_date_end,
            "Scheduled end date on FSM orders should match commitment date.",
        )

        next_route_day = self.sale_order._get_next_route_day()
        self.sale_order.write(
            {
                "commitment_date": next_route_day,
                "commitment_date_end": next_route_day + timedelta(hours=1),
            }
        )

        self.assertEqual(
            next_route_day,
            related_picking.scheduled_date,
            "Scheduled date on pickings should match new commitment date.",
        )

        self.assertEqual(
            next_route_day,
            related_fsm_order.scheduled_date_start,
            "Scheduled start date on FSM orders should match new commitment date.",
        )

        self.assertEqual(
            next_route_day + timedelta(hours=1),
            related_fsm_order.scheduled_date_end,
            "Scheduled end date on FSM orders should match new commitment date.",
        )

        related_fsm_order._compute_postpone_button_visibility()
        self.assertTrue(
            related_fsm_order.show_postpone_button,
            "Postpone button should be visible after confirmation.",
        )

        next_route_day = self.sale_order._get_next_route_day(
            from_date=self.sale_order.commitment_date + timedelta(days=1)
        )
        related_fsm_order.action_postpone_delivery()

        self.assertEqual(
            next_route_day,
            related_picking.scheduled_date,
            "Scheduled date on pickings should match new commitment date.",
        )

        self.assertEqual(
            next_route_day,
            related_fsm_order.scheduled_date_start,
            "Scheduled start date on FSM orders should match new commitment date.",
        )

        self.assertEqual(
            next_route_day + timedelta(hours=1),
            related_fsm_order.scheduled_date_end,
            "Scheduled end date on FSM orders should match new commitment date "
            "and preserve the time.",
        )

    @freeze_time("2025-05-15")
    def test_force_schedule_override(self):
        """
        Test that force_schedule on FSM route allows scheduling on any day.
        """
        # Set route to NOT allow force scheduling
        self.test_route.write({"force_schedule": False})

        # Set an invalid commitment date (not in allowed days)
        invalid_commitment_date = self.sale_order._get_next_route_day() - timedelta(
            days=2
        )
        self.sale_order.commitment_date = invalid_commitment_date

        # Expect validation error because the date is not allowed
        with self.assertRaises(ValidationError):
            self.sale_order._action_confirm()

        # Enable force_schedule on the route
        self.test_route.write({"force_schedule": True})

        # Try confirming the sale order again with the same invalid date
        # This time, no error should be raised
        try:
            self.sale_order._action_confirm()
        except ValidationError:
            self.fail(
                "ValidationError was raised even though force_schedule is enabled."
            )
