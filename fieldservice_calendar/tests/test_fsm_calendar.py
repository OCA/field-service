# Copyright (C) 2021 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMOrder(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Order = cls.env["fsm.order"]
        cls.team = cls.Order._default_team_id()
        cls.team.calendar_user_id = cls.env.ref("base.partner_root").id
        cls.person_id = cls.person_2
        cls.person_id3 = cls.person_3

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

    def test_update_calendar_date_scheduled_date_end(self):
        """Writing scheduled_date_end on the FSM order must sync stop on the
        calendar event (covers the 'scheduled_date_end' branch in
        update_calendar_date)."""
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())

        new_end = fields.Datetime.add(fields.Datetime.today(), hours=5)
        new.write({"scheduled_date_end": new_end})
        self.assertEqual(evt.stop, new_end)

    def test_update_fsm_order_date_recursion_guard(self):
        """Writing a calendar event with recurse_order_calendar=True must not
        propagate the change back to the FSM order (avoids infinite recursion)."""
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())

        # Simulate the write that originates from the FSM order itself; the
        # context flag must short-circuit _update_fsm_order_date.
        evt.with_context(recurse_order_calendar=True).write({"duration": 99})
        # The FSM order must NOT have been updated to 99 h.
        self.assertNotEqual(new.scheduled_duration, 99)

    def test_update_fsm_assigned_recursion_guard(self):
        """Writing partner_ids on a calendar event with recurse_order_calendar=True
        must not propagate the person change back to the FSM order."""
        new = self.Order.create(
            {
                "location_id": self.test_location.id,
                "scheduled_date_start": fields.Datetime.today(),
                "scheduled_duration": 2,
            }
        )
        new.person_id = self.person_id
        evt = new.calendar_event_id
        self.assertTrue(evt.exists())
        original_person = new.person_id

        # Simulate the write that originates from the FSM order itself; the
        # context flag must short-circuit _update_fsm_assigned so it never
        # clears person_id on the FSM order.
        # We remove the worker's partner — without the guard, _update_fsm_assigned
        # would iterate empty fsm_person partners and write person_id=None back.
        evt.with_context(recurse_order_calendar=True).write(
            {"partner_ids": [(3, self.person_id.partner_id.id)]}
        )
        # The FSM order's person must NOT have been cleared.
        self.assertEqual(new.person_id, original_person)

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
            "There should be no other attendees because there is no one assigned",
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
