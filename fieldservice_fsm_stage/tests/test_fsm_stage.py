# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMStage(TransactionCase):
    def setUp(self):
        super(TestFSMStage, self).setUp()
        self.Stage = self.env["fsm.stage"]
        self.Location = self.env["fsm.location"]
        self.Partner = self.env["res.partner"]
        self.Order = self.env["fsm.order"]

    def test_onchange_stage(self):
        stage_1 = self.Stage.create(
            {"name": "To Do", "stage_type": "order", "is_closed": False, "sequence": 1}
        )
        stage_2 = self.Stage.create(
            {"name": "Done", "stage_type": "order", "is_closed": True, "sequence": 2}
        )
        partner = self.Partner.create({"name": "Partner 1"})
        location = self.Location.create({"name": "Location", "owner_id": partner.id})
        order = self.Order.create(
            {"location_id": location.id, "stage_id": stage_1.id, "sequence": 1}
        )
        order.write({"stage_id": stage_2.id})
        today = fields.Date.today()
        closing_date = order.closing_date.date()
        self.assertEqual(today, closing_date)
