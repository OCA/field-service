# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import fields
from odoo.tests.common import TransactionCase


class FSMChangeLogCase(TransactionCase):
    def setUp(self):
        super(FSMChangeLogCase, self).setUp()
        self.cl = self.env["change.log"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.test_location2 = self.env.ref("fieldservice.location_1")
        self.clt = self.env.ref("fieldservice_change_management.change_log_type_1")
        self.impact_med = self.env.ref(
            "fieldservice_change_management.change_log_medium"
        )

    def test_location_wiz(self):
        self.cl.create(
            {
                "name": "Test 1",
                "location_id": self.test_location.id,
                "implemented_on": fields.Datetime.now(),
                "description": "Test description",
                "user_id": self.env.user.id,
                "type_id": self.clt.id,
                "impact_id": self.impact_med.id,
            }
        )
        self.cl.create(
            {
                "name": "Test A",
                "location_id": self.test_location.id,
                "implemented_on": fields.Datetime.now(),
                "description": "Test description",
                "user_id": self.env.user.id,
                "type_id": self.clt.id,
                "impact_id": self.impact_med.id,
            }
        )
        self.test_location.action_open_change_logs()
        self.cl.create(
            {
                "name": "Test 2",
                "location_id": self.test_location2.id,
                "implemented_on": fields.Datetime.now(),
                "description": "Test description",
                "user_id": self.env.user.id,
                "type_id": self.clt.id,
                "impact_id": self.impact_med.id,
            }
        )
        self.test_location2.action_open_change_logs()
