# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMDeliveryTimeRange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.time_range_model = cls.env["fsm.delivery.time.range"]

    def test_create_valid_time_range(self):
        time_range = self.time_range_model.create(
            {
                "start_time": 8.0,
                "end_time": 12.0,
            }
        )
        self.assertEqual(time_range.name, "08:00 - 12:00")

    def test_create_invalid_time_range(self):
        with self.assertRaises(ValidationError):
            self.time_range_model.create(
                {
                    "start_time": 12.0,
                    "end_time": 8.0,
                }
            )

    def test_sequence_ordering(self):
        range1 = self.time_range_model.create(
            {"start_time": 8.0, "end_time": 12.0, "sequence": 10}
        )
        range2 = self.time_range_model.create(
            {"start_time": 13.0, "end_time": 16.0, "sequence": 5}
        )
        time_ranges = self.time_range_model.search([], order="sequence, start_time asc")
        self.assertEqual(time_ranges[0], range2)
        self.assertEqual(time_ranges[1], range1)
