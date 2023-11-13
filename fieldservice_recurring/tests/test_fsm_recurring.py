# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import WEEKLY, rrule

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class FSMRecurringCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(FSMRecurringCase, cls).setUpClass()
        cls.Equipment = cls.env["fsm.equipment"]
        cls.Recurring = cls.env["fsm.recurring"]
        cls.Frequency = cls.env["fsm.frequency"]
        cls.FrequencySet = cls.env["fsm.frequency.set"]
        # create a Partner to be converted to FSM Location/Person
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        # create expected FSM Location to compare to converted FSM Location
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
            }
        )
        cls.rule = cls.Frequency.create(
            {
                "name": "All weekdays",
                "interval_type": "monthly",
                "use_byweekday": True,
                "mo": True,
                "tu": True,
                "we": True,
                "th": True,
                "fr": True,
            }
        )
        cls.fr_set = cls.FrequencySet.create(
            {
                "name": "31th only",
                "schedule_days": 365,
                "fsm_frequency_ids": [(6, 0, cls.rule.ids)],
            }
        )
        cls.fsm_recurring_template = cls.env["fsm.recurring.template"].create(
            {"name": "Test Template"}
        )
        cls.test_equipment = cls.Equipment.create({"name": "Equipment"})

    def test_fsm_recurring_change_states(self):
        recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": self.fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
            }
        )
        recurring.action_start()
        self.assertEqual(recurring.state, "progress")
        recurring.action_suspend()
        self.assertEqual(recurring.state, "suspend")

    def test_cron_generate_orders_rule1(self):
        """Test recurring order with following rule,
        - Work order Monday to Friday, exclude odd week Wednesday
        """
        rules = self.Frequency
        # Frequency Rule for
        rules += self.Frequency.create(
            {
                "name": "All weekdays",
                "interval_type": "monthly",
                "use_byweekday": True,
                "mo": True,
                "tu": True,
                "we": True,
                "th": True,
                "fr": True,
            }
        )
        # Exclusive Rule for odd Wednesday
        for ex in [1, 3, 5]:
            rules += self.Frequency.create(
                {
                    "name": "Exclude Wed-%s" % ex,
                    "is_exclusive": True,
                    "interval_type": "monthly",
                    "use_byweekday": True,
                    "we": True,
                    "use_setpos": True,
                    "set_pos": ex,
                }
            )
        # Frequency Rule Set
        fr_set = self.FrequencySet.create(
            {
                "name": "Monday to Friday, exclude odd Wednesday",
                "schedule_days": 30,
                "fsm_frequency_ids": [(6, 0, rules.ids)],
            }
        )
        # Create Recurring Order link to this rule set
        recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
                "equipment_ids": [(6, 0, [self.test_equipment.id])],
            }
        )
        test_recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "fsm_recurring_template_id": self.fsm_recurring_template.id,
            }
        )
        recurring.action_start()
        test_recurring.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        recurring.onchange_recurring_template_id()
        test_recurring.onchange_recurring_template_id()
        recurring.populate_from_template()
        test_recurring.populate_from_template()
        # Test none of the scheduled date (except on recurring start date),
        # are on weekend or odd wednesday
        all_dates = recurring.fsm_order_ids.filtered(
            lambda l: l.scheduled_date_start != recurring.start_date
        ).mapped("scheduled_date_start")
        days = {x.weekday() for x in all_dates}
        mon_to_fri = {0, 1, 2, 3, 4}
        self.assertTrue(days <= mon_to_fri)

        wednesdays = [x for x in all_dates if x.weekday() == 2]
        first_dom = all_dates[0].replace(day=1)
        odd_wednesdays = list(rrule(WEEKLY, interval=2, dtstart=first_dom, count=3))
        self.assertTrue(wednesdays not in odd_wednesdays)

    def test_cron_generate_orders_rule2(self):
        """Test recurring order with following rule,
        - Work Order every 3 weeks
        """
        rules = self.Frequency
        # Test Rule
        with self.assertRaises(UserError):
            self.Frequency.create(
                {
                    "name": "Every 3 weeks",
                    "interval": 3,
                    "interval_type": "weekly",
                    "use_bymonthday": True,
                    "month_day": 32,
                }
            )
        with self.assertRaises(UserError):
            self.Frequency.create(
                {
                    "name": "Every 3 weeks",
                    "interval": 3,
                    "interval_type": "weekly",
                    "use_setpos": True,
                    "set_pos": 467,
                }
            )
        # Frequency Rule
        rules += self.Frequency.create(
            {"name": "Every 3 weeks", "interval": 3, "interval_type": "weekly"}
        )
        # Frequency Rule Set
        fr_set = self.FrequencySet.create(
            {
                "name": "Every 3 weeks",
                "schedule_days": 100,
                "fsm_frequency_ids": [(6, 0, rules.ids)],
            }
        )
        # Create Recurring Order link to this rule set
        expire_date = datetime.today() + relativedelta(days=-22)
        expire_date1 = datetime.today() + relativedelta(days=+22)
        recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
                "end_date": expire_date1,
            }
        )
        test_recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
                "max_orders": 1,
            }
        )
        test_recurring1 = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
                "max_orders": 1,
            }
        )
        test_recurring1.end_date = expire_date
        recurring.action_start()
        test_recurring.action_start()
        test_recurring1.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        test_recurring._cron_scheduled_task()
        test_recurring1._cron_scheduled_task()
        # Test date are 3 weeks apart (21 days)
        all_dates = recurring.fsm_order_ids.mapped("scheduled_date_start")
        x = False
        for d in all_dates:
            if x:
                diff_days = (d.date() - x.date()).days
                self.assertEqual(diff_days, 21)
            x = d

    def test_cron_generate_orders_rule3(self):
        """Test recurring order with following rule,
        - Work Order every last day of the month only ending by 31th
        """
        rules = self.Frequency
        test = rules.create(
            {
                "name": "31th only",
                "interval": 1,
                "interval_type": "monthly",
                "use_bymonth": True,
                "month_day": 31,
            }
        )
        test._get_rrule()
        # Frequency Rule
        rules += self.Frequency.create(
            {
                "name": "31th only",
                "interval": 1,
                "interval_type": "monthly",
                "use_bymonthday": True,
                "month_day": 31,
            }
        )
        # Frequency Rule Set
        fr_set = self.FrequencySet.create(
            {
                "name": "31th only",
                "schedule_days": 365,
                "fsm_frequency_ids": [(6, 0, rules.ids)],
            }
        )
        # Create Recurring Order link to this rule set
        recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.now().replace(hour=12),
            }
        )
        recurring.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        # Test date are 31st
        all_dates = recurring.fsm_order_ids.filtered(
            lambda l: l.scheduled_date_start != recurring.start_date
        ).mapped("scheduled_date_start")
        for d in all_dates:
            self.assertEqual(d.day, 31)

    def test_fsm_order(self):
        self.test_location = self.env.ref("fieldservice.test_location")
        recurring = self.Recurring.create(
            {
                "fsm_frequency_set_id": self.fr_set.id,
                "location_id": self.test_location.id,
                "start_date": fields.Datetime.today(),
            }
        )
        order_vals = {
            "request_early": fields.Datetime.today(),
            "location_id": self.test_location.id,
            "scheduled_date_start": fields.Datetime.today().replace(
                hour=0, minute=0, second=0
            ),
            "fsm_recurring_id": recurring.id,
        }
        order_vals2 = {
            "request_early": fields.Datetime.today(),
            "location_id": self.test_location.id,
            "scheduled_date_start": fields.Datetime.today().replace(
                hour=0, minute=0, second=0
            ),
        }
        fsm_order = self.env["fsm.order"].create(order_vals)
        self.env["fsm.order"].create(order_vals2)
        fsm_order.action_view_fsm_recurring()
