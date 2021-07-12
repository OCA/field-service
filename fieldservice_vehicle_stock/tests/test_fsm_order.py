# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMOrder(TransactionCase):
    def setUp(self):
        super(TestFSMOrder, self).setUp()
        self.FsmOrder = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")

        currency = self.env["res.currency"].create(
            {
                "name": "Currency 1",
                "symbol": "$",
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        self.company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
                "currency_id": currency.id,
                "partner_id": partner.id,
            }
        )
        self.warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company1.id)], limit=1
        )
        self.test_team = self.env["fsm.team"].create(
            {"name": "Test FSM Team", "company_id": self.company1.id}
        )
        self.product1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "tracking": "serial",
            }
        )
        self.new_pick_type = self.env["stock.picking.type"].create(
            {
                "name": "Stock Picking Type 1",
                "code": "incoming",
                "sequence_code": "SRO",
                "warehouse_id": self.warehouse.id,
                "company_id": self.company1.id,
            }
        )
        self.picking = (
            self.env["stock.picking"]
            .with_context(company_id=self.company1.id)
            .create(
                {
                    "name": "Stock Picking",
                    "location_id": self.test_location.id,
                    "location_dest_id": self.test_location.id,
                    "move_type": "direct",
                    "picking_type_id": self.new_pick_type.id,
                }
            )
        )
        self.vehicle = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 1",
                "inventory_location_id": self.test_location.id,
            }
        )

    def test_assign_vehicle_to_pickings(self):
        order = self.FsmOrder.create(
            {
                "name": "FSM Order 1",
                "location_id": self.test_location.id,
                "company_id": self.company1.id,
                "warehouse_id": self.warehouse.id,
                "team_id": self.test_team.id,
                "inventory_location_id": self.test_location.id,
                "vehicle_id": self.vehicle.id,
                "picking_ids": self.picking.ids,
            }
        )

        self.picking.state = "waiting"
        order.assign_vehicle_to_pickings()
        for pick in order.picking_ids:
            self.assertEqual(order.vehicle_id.id, pick.fsm_vehicle_id.id)
