# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.rrule import rrule, WEEKLY
from odoo import fields
from odoo.tests.common import TransactionCase


class FSMRecurringCase(TransactionCase):

    def setUp(self):
        super(FSMRecurringCase, self).setUp()
        self.Recurring = self.env['fsm.recurring']
        self.Frequency = self.env['fsm.frequency']
        self.FrequencySet = self.env['fsm.frequency.set']
        # create a Partner to be converted to FSM Location/Person
        self.test_loc_partner = self.env['res.partner'].\
            create({
                'name': 'Test Loc Partner',
                'phone': 'ABC',
                'email': 'tlp@email.com',
                })
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env['fsm.location'].\
            create({
                'name': 'Test Location',
                'phone': '123',
                'email': 'tp@email.com',
                'partner_id': self.test_loc_partner.id,
                'owner_id': self.test_loc_partner.id,
                })

    def test_cron_generate_orders_rule1(self):
        """Test recurring order with following rule,
        - Work order Monday to Friday, exclude odd week Wednesday
        """
        rules = self.Frequency
        # Frequency Rule for
        rules += self.Frequency.create({
            'name': 'All weekdays',
            'interval_type': 'monthly', 'use_byweekday': True,
            'mo': True, 'tu': True, 'we': True, 'th': True, 'fr': True,
        })
        # Exclusive Rule for odd Wednesday
        for ex in [1, 3, 5]:
            rules += self.Frequency.create({
                'name': 'Exclude Wed-%s' % ex, 'is_exclusive': True,
                'interval_type': 'monthly', 'use_byweekday': True,
                'we': True, 'use_setpos': True, 'set_pos': ex,
            })
        # Frequency Rule Set
        fr_set = self.FrequencySet.create({
            'name': 'Monday to Friday, exclude odd Wednesday',
            'schedule_days': 30,
            'fsm_frequency_ids': [(6, 0, rules.ids)]
        })
        # Create Recurring Order link to this rule set
        recurring = self.Recurring.create({
            'fsm_frequency_set_id': fr_set.id,
            'location_id': self.test_location.id,
            'start_date': fields.Datetime.today(),
        })
        recurring.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        # Test none of the scheduled date (except on recurring start date),
        # are on weekend or odd wednesday
        all_dates = recurring.fsm_order_ids.filtered(
            lambda l: l.scheduled_date_start != recurring.start_date).\
            mapped('scheduled_date_start')
        days = set([x.weekday() for x in all_dates])
        mon_to_fri = set([0, 1, 2, 3, 4])
        self.assertTrue(days <= mon_to_fri)

        wednesdays = [x for x in all_dates if x.weekday() == 2]
        first_dom = all_dates[0].replace(day=1)
        odd_wednesdays = list(
            rrule(WEEKLY, interval=2, dtstart=first_dom, count=3)
        )
        self.assertTrue(wednesdays not in odd_wednesdays)

    def test_cron_generate_orders_rule2(self):
        """Test recurring order with following rule,
        - Work Order every 3 weeks
        """
        rules = self.Frequency
        # Frequency Rule
        rules += self.Frequency.create({
            'name': 'Every 3 weeks',
            'interval': 3, 'interval_type': 'weekly',
        })
        # Frequency Rule Set
        fr_set = self.FrequencySet.create({
            'name': 'Every 3 weeks',
            'schedule_days': 100,
            'fsm_frequency_ids': [(6, 0, rules.ids)]
        })
        # Create Recurring Order link to this rule set
        recurring = self.Recurring.create({
            'fsm_frequency_set_id': fr_set.id,
            'location_id': self.test_location.id,
            'start_date': fields.Datetime.today(),
        })
        recurring.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        # Test date are 3 weeks apart (21 days)
        all_dates = recurring.fsm_order_ids.mapped('scheduled_date_start')
        x = False
        for d in all_dates:
            if x:
                diff_days = (d-x).days
                self.assertEqual(diff_days, 21)
            x = d

    def test_cron_generate_orders_rule3(self):
        """Test recurring order with following rule,
        - Work Order every last day of the month only ending by 31th
        """
        rules = self.Frequency
        # Frequency Rule
        rules += self.Frequency.create({
            'name': '31th only',
            'interval': 1, 'interval_type': 'monthly',
            'use_bymonthday': True, 'month_day': 31,
        })
        # Frequency Rule Set
        fr_set = self.FrequencySet.create({
            'name': '31th only',
            'schedule_days': 365,
            'fsm_frequency_ids': [(6, 0, rules.ids)]
        })
        # Create Recurring Order link to this rule set
        recurring = self.Recurring.create({
            'fsm_frequency_set_id': fr_set.id,
            'location_id': self.test_location.id,
            'start_date': fields.Datetime.today(),
        })
        recurring.action_start()
        # Run schedule job now, to compute the future work orders
        recurring._cron_scheduled_task()
        # Test date are 31st
        all_dates = recurring.fsm_order_ids.filtered(
            lambda l: l.scheduled_date_start != recurring.start_date).\
            mapped('scheduled_date_start')
        for d in all_dates:
            self.assertEqual(d.day, 31)
