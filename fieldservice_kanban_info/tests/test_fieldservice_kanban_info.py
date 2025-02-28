# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestFieldServiceKanbanInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FSMOrder = cls.env["fsm.order"]
        cls.config_param = cls.env["ir.config_parameter"].sudo()
        cls.location = cls.env.ref("fieldservice.test_location")
        cls.now = fields.Datetime.now()
        cls.lang = cls.env.user.lang

    def _create_order(self, start=None, end=None):
        order = self.FSMOrder.create(
            {
                "scheduled_date_start": start,
                "scheduled_date_end": end,
                "location_id": self.location.id,
            }
        )
        order._compute_schedule_time_range()
        return order

    def test_schedule_time_range_time_only_same_day(self):
        self.config_param.set_param(
            "fieldservice.schedule_time_range_format", "time_only"
        )
        order = self._create_order(self.now, self.now + relativedelta(hours=2))
        self.assertIn("-", order.schedule_time_range)

    def test_schedule_time_range_date_and_time_same_day(self):
        self.config_param.set_param(
            "fieldservice.schedule_time_range_format", "date_and_time"
        )
        order = self._create_order(self.now, self.now + relativedelta(hours=2))
        self.assertIn("/", order.schedule_time_range)
        self.assertIn("-", order.schedule_time_range)

    def test_schedule_time_range_no_start_date(self):
        order = self._create_order()
        self.assertFalse(order.schedule_time_range)

    def test_schedule_time_range_us_format(self):
        """Test %m/%d/%Y %I:%M %p (US format with AM/PM)"""
        self.env.user.lang = "en_US"
        self.env["res.lang"]._lang_get("en_US").write(
            {"date_format": "%m/%d/%Y", "time_format": "%I:%M %p"}
        )
        self.config_param.set_param(
            "fieldservice.schedule_time_range_format", "date_and_time"
        )

        order = self._create_order(self.now, self.now + relativedelta(hours=2))
        self.assertRegex(
            order.schedule_time_range,
            r"\d{2}/\d{2}/\d{4} \d{2}:\d{2} (AM|PM) - \d{2}:\d{2} (AM|PM)",
        )

    def test_schedule_time_range_eu_format(self):
        """Test %d/%m/%Y %H:%M:%S (EU format with seconds)"""
        self.env["res.lang"]._activate_lang("es_ES")
        self.env.user.lang = "es_ES"
        self.env["res.lang"]._lang_get("es_ES").write(
            {"date_format": "%d/%m/%Y", "time_format": "%H:%M:%S"}
        )
        self.config_param.set_param(
            "fieldservice.schedule_time_range_format", "date_and_time"
        )

        order = self._create_order(self.now, self.now + relativedelta(hours=2))
        self.assertRegex(
            order.schedule_time_range, r"\d{2}/\d{2}/\d{4} \d{2}:\d{2} - \d{2}:\d{2}"
        )
