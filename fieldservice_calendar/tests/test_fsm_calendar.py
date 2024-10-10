# Copyright (C) 2021 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestFSMOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Order = cls.env["fsm.order"]
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.location_1 = cls.env.ref("fieldservice.location_1")
        cls.team = cls.Order._default_team_id()
        cls.team.calendar_user_id = cls.env.ref("base.partner_root").id
        cls.person_id = cls.env.ref("fieldservice.person_2")
        cls.person_id3 = cls.env.ref("fieldservice.person_3")

    def test_fsm_order_no_duration(self):
        # not scheduled (no duration) = no calendar
        new = self._create_fsm_order(schedule=False)
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())

    def test_fsm_order_no_calendar_user(self):
        self.team.calendar_user_id = False
        # no calendar user_id  = no calendar event
        new = self._create_fsm_order(schedule=True)
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())
        self.team.calendar_user_id = self.env.ref("base.partner_root").id

        # update order
        new.write({"scheduled_duration": 3})
        new.write({"location_id": self.location_1.id})
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())
        evt.with_context(recurse_order_calendar=False).write({"duration": 5})
        # ensure deletion
        new.scheduled_date_start = False
        evt = new.calendar_event_id
        self.assertFalse(evt.exists())

    def test_fsm_order_unlink(self):
        new = self._create_fsm_order(schedule=True)
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())

        # delete the order
        new.unlink()
        # ensure the evt is deleted
        # this test may fail if another module
        # archive instead of unlink (like gcalendar)
        self.assertFalse(evt.exists())

    def test_fsm_order_ensure_attendee(self):
        new = self._create_fsm_order(schedule=True)
        evt = new.calendar_event_id
        self.assertTrue(
            len(evt.partner_ids) == 1,
            "There should be no other attendees" " because there is no one assigned",
        )
        # organiser is attendee
        new.person_id = self.person_id
        evt.with_context(recurse_order_calendar=False).write({"partner_ids": []})
        self.assertTrue(self.person_id.partner_id in evt.partner_ids)
        new.person_id = self.person_id3
        self.assertTrue(self.person_id3.partner_id in evt.partner_ids)
        self.assertTrue(
            len(evt.partner_ids) == 2, "Not workers should be removed from attendees"
        )

    def test_description_sync(self):
        fsm_order = self._create_fsm_order(schedule=True)
        event = fsm_order.calendar_event_id
        self.assertEqual(event.description, "<p></p>")
        with Form(fsm_order) as form:
            form.description = "line 1\nline 2"
        self.assertEqual(event.description, "<p>line 1<br>line 2</p>")
        with Form(event) as form:
            form.description = "<p>line 1<br>line 2<br>line 3</p>"
        self.assertEqual(fsm_order.description, "line 1\nline 2\nline 3")

    def _create_fsm_order(self, schedule=False):
        form = Form(self.Order)
        form.location_id = self.test_location
        if schedule:
            form.scheduled_date_start = fields.Datetime.today()
            form.scheduled_duration = 2
        return form.save()
