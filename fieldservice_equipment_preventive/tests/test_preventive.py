# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestEquipmentPreventive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env.user)
        cls.location = cls.env.ref("fieldservice.test_location")
        cls.maintenance = cls.env.ref(
            "fieldservice_equipment_preventive.preventive_type_maintenance"
        )
        cls.calibration = cls.env.ref(
            "fieldservice_equipment_preventive.preventive_type_calibration"
        )
        cls.order_type = cls.env["fsm.order.type"].create({"name": "Calibration"})
        cls.calibration.order_type_id = cls.order_type
        frequency = cls.env["fsm.frequency"].create(
            {"name": "Monthly", "interval": 1, "interval_type": "monthly"}
        )
        cls.frequency_set = cls.env["fsm.frequency.set"].create(
            {
                "name": "Monthly",
                "schedule_days": 45,
                "fsm_frequency_ids": [(6, 0, frequency.ids)],
            }
        )
        cls.template = cls.env["fsm.template"].create({"name": "Calibration sheet"})
        Equipment = cls.env["fsm.equipment"]
        common = {"current_location_id": cls.location.id}
        # monthly maintenance overdue, yearly calibration never done
        cls.autoclave = Equipment.create(
            {
                **common,
                "name": "Autoclave",
                "preventive_ids": [
                    (
                        0,
                        0,
                        {
                            "type_id": cls.maintenance.id,
                            "interval": 1,
                            "last_date": cls.today - relativedelta(months=3),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "type_id": cls.calibration.id,
                            "interval": 12,
                            "template_id": cls.template.id,
                        },
                    ),
                ],
            }
        )
        cls.recent = Equipment.create(
            {
                **common,
                "name": "Recent",
                "preventive_ids": [
                    (
                        0,
                        0,
                        {
                            "type_id": cls.maintenance.id,
                            "interval": 12,
                            "last_date": cls.today,
                        },
                    )
                ],
            }
        )
        cls.none = Equipment.create({**common, "name": "None"})
        cls.pm = cls.autoclave.preventive_ids.filtered(
            lambda p: p.type_id == cls.maintenance
        )
        cls.cal = cls.autoclave.preventive_ids - cls.pm
        cls.recurring = cls.env["fsm.recurring"].create(
            {
                "location_id": cls.location.id,
                "fsm_frequency_set_id": cls.frequency_set.id,
                "is_preventive": True,
                "start_date": fields.Datetime.now(),
            }
        )

    def test_next_dates(self):
        self.assertEqual(self.pm.next_date, self.today - relativedelta(months=2))
        self.assertEqual(self.cal.next_date, self.today)
        self.assertEqual(self.autoclave.next_preventive_date, self.pm.next_date)
        self.assertFalse(self.none.next_preventive_date)

    def test_equipments_of_the_plan(self):
        self.assertEqual(self.recurring.preventive_equipment_count, 2)
        action = self.recurring.action_view_preventive_equipments()
        self.assertEqual(
            self.env["fsm.equipment"].search(action["domain"]),
            self.autoclave + self.recent,
        )
        # only the calibration of the autoclave has a template
        self.assertEqual(self.recurring.preventive_no_template_count, 2)
        action = self.recurring.action_view_preventive_no_template()
        self.assertEqual(
            self.env["fsm.equipment"].search(action["domain"]),
            self.autoclave + self.recent,
        )
        self.recurring.preventive_type_ids = self.calibration
        self.assertEqual(self.recurring.preventive_equipment_count, 1)
        self.assertEqual(self.recurring.preventive_no_template_count, 0)

    def test_visits(self):
        self.recurring.action_start()
        orders = self.recurring.fsm_order_ids.sorted("scheduled_date_start")
        self.assertEqual(len(orders), 2)
        first, second = orders
        # both visit types of the equipment in the same order, most overdue first
        self.assertEqual(
            first.equipment_line_ids.preventive_id.ids, (self.pm + self.cal).ids
        )
        self.assertEqual(first.equipment_ids, self.autoclave)
        self.assertEqual(first.equipment_line_ids.mapped("template_id"), self.template)
        self.assertFalse(first.type)
        # the monthly visit is planned again, the yearly one is not
        self.assertEqual(second.equipment_line_ids.preventive_id, self.pm)
        first.equipment_line_ids[0].action_done()
        self.assertEqual(self.pm.last_date, self.today)
        # what was not done goes on top of the following visit
        first.action_complete()
        self.assertEqual(
            second.equipment_line_ids.sorted().preventive_id.ids,
            (self.cal + self.pm).ids,
        )
        # the last visit has nowhere to carry over to
        second.action_complete()
        self.assertEqual(len(second.equipment_line_ids), 2)

    def test_single_type_sets_order_type(self):
        self.recurring.preventive_type_ids = self.calibration
        self.recurring.action_start()
        order = self.recurring.fsm_order_ids.sorted("scheduled_date_start")[0]
        self.assertEqual(order.equipment_line_ids.preventive_type_id, self.calibration)
        self.assertEqual(order.type, self.order_type)

    def test_regular_recurring_untouched(self):
        self.recurring.is_preventive = False
        self.assertFalse(self.recurring.preventive_equipment_count)
        self.recurring.equipment_ids = self.none
        self.recurring.action_start()
        order = self.recurring.fsm_order_ids[0]
        self.assertEqual(order.equipment_ids, self.none)
        self.assertFalse(order.equipment_line_ids)
        order.action_complete()
