# Copyright (C) 2021 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMOrder(TransactionCase):
    def setUp(self):
        super(TestFSMOrder, self).setUp()
        self.Order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.team = self.Order._default_team_id()
        self.team.calendar_user_id = self.env.ref("base.partner_root").id
        self.person_id = self.env.ref("fieldservice.person_2")
        self.person_id3 = self.env.ref("fieldservice.person_3")

    def test_fsm_order_no_duration(self):
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                # no duration = no calendar
            }
        )
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())

    def test_fsm_order_no_calendar_user(self):
        self.team.calendar_user_id = False
        # no calendar user_id  = no calendar event
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())
        self.team.calendar_user_id = self.env.ref("base.partner_root").id

        # update order
        new.scheduled_duration = 3
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())

        # ensure deletion
        new.scheduled_date_start = False
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())

    def test_fsm_order_unlink(self):
        # Create an Orders
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())

        # delete the order
        new.unlink()
        # ensure the evt is deleted
        # this test may fail if another module
        # archive instead of unlink (like gcalendar)
        self.assertFalse(evt.exists())

    def test_fsm_order_ensure_attendee(self):
        # Create an Orders
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        evt = new.calendar_event_id

        self.assertTrue(
            len(evt.partner_ids) == 1,
            "There should be no other attendees" " because there is no one assigned",
        )
        # organiser is attendee
        new.person_id = self.person_id
        self.assertTrue(self.person_id.partner_id in evt.partner_ids)
        new.person_id = self.person_id3
        self.assertTrue(self.person_id3.partner_id in evt.partner_ids)
        self.assertTrue(
            len(evt.partner_ids) == 2, "Not workers should be removed from attendees"
        )
