# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestPreventiveAgreement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("fieldservice.test_location")
        cls.agreement = cls.env["agreement"].create(
            {"name": "Agreement", "code": "PREV-AGR"}
        )
        frequency = cls.env["fsm.frequency"].create(
            {"name": "Monthly", "interval": 1, "interval_type": "monthly"}
        )
        frequency_set = cls.env["fsm.frequency.set"].create(
            {
                "name": "Monthly",
                "schedule_days": 10,
                "fsm_frequency_ids": [(6, 0, frequency.ids)],
            }
        )
        maintenance = cls.env.ref(
            "fieldservice_equipment_preventive.preventive_type_maintenance"
        )
        cls.common = {
            "current_location_id": cls.location.id,
            "preventive_ids": [(0, 0, {"type_id": maintenance.id, "interval": 1})],
        }
        common = cls.common
        cls.covered = cls.env["fsm.equipment"].create(
            {**common, "name": "Covered", "agreement_id": cls.agreement.id}
        )
        cls.other = cls.env["fsm.equipment"].create({**common, "name": "Other"})
        cls.recurring = cls.env["fsm.recurring"].create(
            {
                "location_id": cls.location.id,
                "fsm_frequency_set_id": frequency_set.id,
                "is_preventive": True,
                "start_date": fields.Datetime.now(),
            }
        )

    def test_available_agreements(self):
        self.env["agreement"].create({"name": "Elsewhere", "code": "PREV-ELSE"})
        self.assertEqual(
            self.recurring.preventive_available_agreement_ids, self.agreement
        )
        # the only agreement of the location is preselected
        self.recurring._onchange_preventive_agreement_location()
        self.assertEqual(self.recurring.preventive_agreement_id, self.agreement)
        # with more than one the choice is left to the user
        second = self.env["agreement"].create({"name": "Second", "code": "PREV-2ND"})
        self.other.agreement_id = second
        self.recurring.preventive_agreement_id = False
        self.recurring.invalidate_recordset(["preventive_available_agreement_ids"])
        self.recurring._onchange_preventive_agreement_location()
        self.assertFalse(self.recurring.preventive_agreement_id)
        self.recurring.preventive_agreement_id = self.agreement
        self.recurring._onchange_preventive_agreement_location()
        self.assertEqual(self.recurring.preventive_agreement_id, self.agreement)
        # an agreement that does not fit the visit is dropped
        self.recurring.is_preventive = False
        self.assertFalse(self.recurring.preventive_available_agreement_ids)
        self.recurring._onchange_preventive_agreement_location()
        self.assertFalse(self.recurring.preventive_agreement_id)

    def test_agreement_rules(self):
        calibration = self.env.ref(
            "fieldservice_equipment_preventive.preventive_type_calibration"
        )
        manual = self.covered.preventive_ids
        template = self.env["fsm.template"].create({"name": "Calibration sheet"})
        rule = self.env["agreement.preventive.rule"].create(
            {
                "agreement_id": self.agreement.id,
                "type_id": calibration.id,
                "interval": 6,
                "template_id": template.id,
            }
        )
        visit = self.covered.preventive_ids - manual
        self.assertEqual(visit.template_id, template)
        self.assertEqual((visit.type_id, visit.interval), (calibration, 6))
        self.assertFalse(self.other.preventive_ids - self.other.preventive_ids[:1])
        # a second rule for the same type never applies: the first one wins
        self.env["agreement.preventive.rule"].create(
            {
                "agreement_id": self.agreement.id,
                "type_id": calibration.id,
                "interval": 24,
                "sequence": 99,
            }
        )
        self.assertEqual(visit.interval, 6)
        # the interval follows the rule and the registered dates are kept
        visit.last_date = fields.Date.today()
        rule.interval = 12
        self.assertEqual((visit.interval, visit.last_date), (12, fields.Date.today()))
        # equipments entering and leaving the agreement
        self.other.agreement_id = self.agreement
        self.assertIn(calibration, self.other.preventive_ids.type_id)
        self.other.agreement_id = False
        self.assertNotIn(calibration, self.other.preventive_ids.type_id)
        new = self.env["fsm.equipment"].create(
            {"name": "New", "agreement_id": self.agreement.id}
        )
        self.assertEqual(new.preventive_ids.type_id, calibration)
        new.name = "Renamed"
        # without rules only the visits added by hand remain
        self.agreement.preventive_rule_ids.unlink()
        self.assertEqual(self.covered.preventive_ids, manual)

    def test_agreement_required(self):
        self.env.company.preventive_agreement_required = True
        with self.assertRaises(ValidationError):
            self.recurring.copy()
        self.recurring.preventive_agreement_id = self.agreement
        with self.assertRaises(ValidationError):
            self.recurring.preventive_agreement_id = False
        # regular recurring orders are not concerned
        self.recurring.write({"is_preventive": False, "preventive_agreement_id": False})

    def test_without_agreement(self):
        self.assertEqual(self.recurring.preventive_equipment_count, 2)
        self.recurring.action_start()
        order = self.recurring.fsm_order_ids[0]
        self.assertEqual(order.equipment_ids, self.covered + self.other)
        self.assertFalse(order.agreement_id)

    def test_with_agreement(self):
        self.recurring.preventive_agreement_id = self.agreement
        self.assertEqual(self.recurring.preventive_equipment_count, 1)
        self.recurring.action_start()
        order = self.recurring.fsm_order_ids[0]
        self.assertEqual(order.equipment_ids, self.covered)
        self.assertEqual(order.agreement_id, self.agreement)

    def test_multi_company(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        self.env["fsm.equipment"].create(
            {
                **self.common,
                "name": "Foreign",
                "company_id": other_company.id,
                "agreement_id": self.agreement.id,
            }
        )
        # equipments of another company are not covered, with or without agreement
        self.assertEqual(self.recurring.preventive_equipment_count, 2)
        self.recurring.preventive_agreement_id = self.agreement
        self.assertEqual(self.recurring.preventive_equipment_count, 1)
        # the agreement requirement is set per company
        other_company.preventive_agreement_required = True
        self.recurring.preventive_agreement_id = False
        self.assertFalse(self.recurring.preventive_agreement_required)
        with self.assertRaises(ValidationError):
            self.recurring.company_id = other_company
