# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestFsmOrderSurveySubmit(TransactionCase):
    def setUp(self):
        super(TestFsmOrderSurveySubmit, self).setUp()
        self.test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        self.fsm_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
            }
        )

    def test_action_submit_fsm_order_survey(self):
        result = self.fsm_order.action_submit_fsm_order_survey()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["res_model"], "fsm.order.survey.submit")
        self.assertEqual(result["target"], "new")
        self.assertEqual(result["name"], "Submit Survey ")

    def test_action_open_survey_inputs(self):
        result = self.fsm_order.action_open_survey_inputs()
        expected_url = "/fsm_order/{}/results/".format(self.fsm_order.id)
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertEqual(result["name"], "Survey Answer")
        self.assertEqual(result["target"], "self")
        self.assertEqual(result["url"], expected_url)
