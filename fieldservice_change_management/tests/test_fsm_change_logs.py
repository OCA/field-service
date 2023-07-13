# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import fields
from odoo.tests.common import TransactionCase


class FSMChangeLogCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(FSMChangeLogCase, cls).setUpClass()
        cls.cl = cls.env["change.log"]
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.test_location2 = cls.env.ref("fieldservice.location_1")
        cls.clt = cls.env.ref("fieldservice_change_management.change_log_type_1")
        cls.impact_med = cls.env.ref("fieldservice_change_management.change_log_medium")

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
