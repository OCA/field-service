# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestFSMOrder(TransactionCase):
    def setUp(self):
        super(TestFSMOrder, self).setUp()
        self.Order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.maintenance_order_type = self.env["fsm.order.type"].create(
            {"name": "Maintenance Request", "internal_type": "maintenance"}
        )
        self.maintenance_team = self.env["maintenance.team"].create(
            {"name": "Test Maintenance Team", "company_id": self.env.user.company_id.id}
        )
        self.test_equipment = self.env["fsm.equipment"].create(
            {
                "name": "Test Equipment",
                "company_id": self.env.user.company_id.id,
                "maintenance_team_id": self.maintenance_team.id,
            }
        )

    def test_fsm_order(self):
        # Create an Orders that generates Maintenance Request
        view_id = "fieldservice.fsm_order_form"
        hours_diff = 100
        with Form(self.Order, view=view_id) as f:
            f.location_id = self.test_location
            f.date_start = fields.Datetime.today()
            f.date_end = f.date_start + timedelta(hours=hours_diff)
            f.request_early = fields.Datetime.today()
            f.type = self.maintenance_order_type
            f.equipment_id = self.test_equipment
        order = f.save()
        maintenance_request = self.env["maintenance.request"].search(
            [("name", "=", order.name)]
        )
        self.assertTrue(maintenance_request)
